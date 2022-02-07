#include <arpa/inet.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <signal.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <sys/types.h>
#include <fcntl.h>

#define LOKAL_PORT 80
#define BAK_LOGG 10 //Størrelse på køen av ventende forespørsler
#define BUF_SIZE 1024 //Størrelse på buffer, 1kb

typedef struct sporring {
	char*method;
	char*url;
	char*url_extension;
	char*content_type;
} spr_info;

int fd_from_file(char*filpath) {
	int fd;
	if (0 == access(filpath, R_OK)) {
		fd = open(filpath, O_RDONLY);
		if (-1 == fd)
			printf("ERROR: failed to open file: %s\n", filpath);
		return fd;
	}
	else return -1;
}

int main() {

//Demonisering
	pid_t process_id = 0;
	pid_t sid = 0;

	//Lager barneprosess
	process_id = fork();

	//Tester om fork feilet
	if (process_id < 0) {
		printf("fork failed!\n");
		exit(1);
	}

	//Dreper foreldreprosessen
	if (process_id != 0) {
		printf("process_id of child process %d \n", process_id);
		exit(0);
	}

	//Ignorerer SIGHUP-signal fra prosessgruppeleder
	signal(SIGHUP, SIG_IGN);

	//Gjør prosessen til sesjonsleder og frigjør fra terminal
	sid = setsid();

	if (sid < 0) {
		printf("setsid failed");
		exit(1);
	}

	//Oppretter ny barneprosess og avslutter eksisterende
	process_id = fork();
	if (process_id != 0) {
		printf("process_id of child process %d \n", process_id);
		exit(0);
	}

	printf("A daemon has spawned!\nGoing dark...\n");

        //Resetter file mode creation mask
        umask(0);

	//Stenger stdin, stdout og stderr
	close(STDIN_FILENO);
	close(STDOUT_FILENO);
	close(STDERR_FILENO);

	//Stenger alle åpne fildeskriptorer. Kilde: stackoverflow
	for (int x = sysconf(_SC_OPEN_MAX); x >= 0; x--)
		if (x != 2 || x != 1)
			close(x);

//HTTP-Server
	struct stat *mime_size;
        struct sockaddr_in lok_adr;
        int server_fd, ny_server_fd, err_fd, mime_fd;
	char*mime_types_buffer;

        //Lager socket
        server_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

        //Hindre at operativsystemet ikke reserverer porten etter httptjener er ferdig.
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &(int){ 1 }, sizeof(int));

        //initierer lokal adresse
        lok_adr.sin_family      = AF_INET;
        lok_adr.sin_port        = htons((u_short)LOKAL_PORT);
        lok_adr.sin_addr.s_addr = htonl(INADDR_ANY);

	//Endrer arbeidskatalog til webroot
	//chdir("/var/www/");

	//åpner fd til loggfil, dersom filen ikke eksisterer opprettes den
	err_fd = open("error.log", O_RDWR | O_CREAT | O_APPEND, S_IRWXU);
	if (-1 == err_fd) {
		fprintf(stderr, "ERROR: åpning/opprettelse av errorfil feilet.");
		exit(1);
	}
	dup2(err_fd, 2); // Dirigerer stderr til errorfil
	close(err_fd);

	//Oppretter fd for mime.types og leser til array
	mime_fd = fd_from_file("/etc/mime.types");
	mime_size = malloc(sizeof(struct stat));
	fstat(mime_fd, mime_size);
	mime_types_buffer = (char*) malloc(mime_size->st_size +1); // for nullterminating byte

	fprintf(stderr, "INFO: Stat filesize returns: %ld\n", mime_size->st_size);

	if (-1 == read(mime_fd, mime_types_buffer, mime_size->st_size))
		fprintf(stderr, "ERROR: Failed while reading mime_fd\n");

	close(mime_fd);
	free(mime_size);
	strcat(mime_types_buffer, "\0"); // legger til nullterminering

	// Kobler sammen socket og lokal adresse
        if (bind(server_fd, (struct sockaddr *) &lok_adr, sizeof(lok_adr))==0)
                fprintf(stderr, "Process %d is bound to port %d.\n", getpid(), LOKAL_PORT);
        else
		exit(1);

        //Venter på http forespørsel om forbindelse
        listen(server_fd, BAK_LOGG);
        fprintf(stderr, "Venter på klient forespørsel...\n\n");

	//Endrer bruker og gruppe fra root til kali
	//setuid();
	//setgid();

	while(1){

                //aksepterer mottatt forespørsel
                ny_server_fd = accept(server_fd, NULL, NULL);

                if(0==fork()) {

			fprintf(stderr, "Ny tilkobling, prosess-id: %d/n", getpid());

			int inc_buf_size = 0;
			char*inc_buf = (char*)malloc(BUF_SIZE),
					*out_buf = (char*)malloc(BUF_SIZE);
			spr_info*request = malloc(sizeof(spr_info));

                        dup2(ny_server_fd, 1); //socket sender tilbake til forespørsel

			inc_buf_size = read(ny_server_fd, inc_buf, BUF_SIZE);

			if (-1 == inc_buf_size) {
				fprintf(stderr, "ERROR: Kunne ikke lese ny_server_fd\navslutter program\n");
				shutdown(ny_server_fd, SHUT_RDWR);
				exit(1);
			}

			split_request(inc_buf, inc_buf_size);


			get_file_extension(request);


			send_response(request, mime_types_buffer);
/*			printf("HTTP/1.1 200 OK \n");//todo endre til asis filer sending
                        printf("Content-type: text/plain\n");
                        printf("\n");
                        printf("Heisann Klient!\n");
*/
                        fflush(stdout);
                        //Sørger for å stenge socket for skriving og lesing
                        // NB! Frigjør ingen plass i fildeskriptortabellen
                        shutdown(ny_server_fd, SHUT_RDWR);

                        exit(0);
                }

                else {
                        close(ny_server_fd);
                }
        }
        return 0;
}
