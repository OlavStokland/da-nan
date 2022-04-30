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
#define BUF_SIZE 65536 //Størrelse på buffer, 64kb

//struct for å splitte en http-forespørsel
typedef struct sporring {
	char*method;
	char*url;
	char*url_extension;
	char*content_type;
} spr_info;

//Metode for å åpne fil
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

//Metode for å lese fil til buffer
char*file_reader(char*file_path) {
        struct stat*file = malloc(sizeof(struct stat));
        int respons_fd;
        char*buffer;

        respons_fd = fd_from_file(file_path);
        fstat(respons_fd, file);
        buffer = (char*) malloc(file->st_size+1);

        if (-1 == read(respons_fd, buffer, file->st_size))
                fprintf(stderr, "ERROR: Could not read: %s\n", file_path);
        strcat(buffer, "\0");

        close(respons_fd);
        free(file);

        return buffer;
}

//Metode for å skrive ut http-feilmeldinger
void func_error(char*error_msg, int error_code) {
	printf("HTTP/1.1 %d Not Found\n", error_code);
	printf("Content-Type: plain/text; charset=UTF-8\n");
	printf("Connection: Closed\n");
	printf("\n");
	printf("%d: %s\n", error_code, error_msg);
}

//Metode for å skrive ut http-melding
void func_wrap(int size_of_content, char*body, spr_info*request) {
	printf("HTTP/1.1 200 OK\n");
	printf("Content-Type: %s; charset=UTF-8\n", request->content_type);
	printf("Connection: Closed\n");
	printf("Content-Length: %d;\n", size_of_content);
	printf("\n");
	printf("%s", body);
}

//Metode for å splitte en innkommende http request
void split_request(char*req_str, spr_info*request) {
        request->method = strtok(req_str, " ");
        request->url = strtok(NULL, " ");
}

//Metode for å finne filtype (.xxx) som spørres etter og plasserer dette i structen. Returnerer 0, -1 eller 1 til kallende program avhengig av om det spørres etter filtype eller ikke
int get_file_extension(spr_info*request) {

	//ingen spesifikk fil etterspørres, kun en side
        if (!strcmp(request->url, "/"))
                return 0;

	//plasserer alt etter siste punktum i url_extension i structen
        request->url_extension = strrchr(request->url, '/');
        request->url_extension = strrchr(request->url_extension, '.');

	//Ingen verdi ble lagt i url_extension
        if (!request->url_extension)
                return -1;
        else
                return 1;
}

//Metode for å sjekke filtype det spørres etter mot mime-types, samt content-type. Returnerer 1 til kallende program hvis match
int req_fileCheck(spr_info*request, char*mime_buf) {

	// Dersom asis fil
	if (!strcmp("asis", request->url_extension+1))
		return 1;

  	char*line, *ptr, *r = NULL, *p = NULL,
			*buffer = (char*) malloc(strlen(mime_buf));
	strcpy(buffer, mime_buf);

	//Leser mime-types linje for linje og sjekker om det er match med filtype det spørres etter. Oppdaterer også content-type for bruk i HTTP-responsen
	line = strtok_r(buffer, "\t\n", &r);
	while (line) {
		ptr = strtok_r(line, " ", &p);

		while (ptr) {
			if (!strcmp(ptr, request->url_extension+1)) {
				request->content_type = line; //putter korrekt content type i structen
				return 1;
			}
			ptr = strtok_r(NULL, " ", &p);
		}
		line = strtok_r(NULL, "\t\n", &r);
	}
	return 0;
}

//Metode for å svare på en HTTP-forespørsel
void send_response(int sd, spr_info*request, char*mime_buf) {

	FILE*fptr;
	char response[BUF_SIZE];
	char*buffer;
	char*defaultPage = "/index.html";
	int respons_fd = 0, match = 0;

	// Det er en verdi i url_extension -> det er en fil som etterspørres
	if (request->url_extension) {

		// printer ut asis filen hvis det er denne som etterspørres
		if (!strcmp("asis", request->url_extension+1)) {
			printf("%s", file_reader(request->url));
			return;
		}

		//Kaller på metoden for å sjekke om filtypen  finnes i mimetypes, og dermed støttes: returnerer 1 hvis lovlig filtype
		match = req_fileCheck(request, mime_buf);

		// Ikke match med mimetypes - filtypen støttes ikke, skriver ut HTTP error 415
		if (match == 0) {
			func_error("File type not supported", 415);
		}

		// Gyldig filtype
		else if (match == 1) {
			respons_fd = fd_from_file(request->url);
			if (-1 == respons_fd) { //filen kan ikke aksesseres eller finnes ikke
				fprintf(stderr, "ERROR: %s: No access, or file not found\n", request->url);
				func_error("The file type is supported, but no file could be found..", 404);
			}
			else {
				struct stat*files = malloc(sizeof(struct stat));
        			int response_fd;
				char*header;
				
				//finner lengden på filen med fd_from_file-metoden og fstat
			        response_fd = fd_from_file(request->url);
			        fstat(response_fd, files);
				
				//Åpner filen som er forespurt
				fptr = fopen(request->url, "r");
				
				//Skriver HTTP-header til variabel header
				sprintf(header, "HTTP/1.1 200 OK\nContent-Type: %s; charset=UTF-8\nConnection: Closed\nContent-Length: %d;\n\n", request->content_type,files->st_size);
				
				//Sender header til socket
				send(sd, header, strlen(header), 0);

				//HTTP-kropp. Løkke som leser fil til buffer og sender til socket. Løkken går til hele filen er lest og sendt
				size_t read_bytes;
        			while ((read_bytes = fread(response, 1, BUF_SIZE, fptr)) > 0) {
			            	send(sd, response, read_bytes, 0);
        			}
			        fclose(fptr); //lukker filen
			}
			close(respons_fd);
		}
	}
        // Ingen spesifikke filer eller sider etterspørres - rediriger til index
        else if (strcmp(request->url,"/")==0) {
                fprintf(stderr, "INFO: No page requested, redirecting to index\n");
		buffer = file_reader(defaultPage);
                func_wrap(strlen(buffer)+1, buffer, request);
                free(buffer);
        }

	//Siden finnes ikke
	else if (request->url && !request->url_extension)
		func_error("Page not found", 404);

}

static void daemonizeProcess () { //Demonisering

	pid_t process_id = 0;
	pid_t sid = 0;

	//Lager barneprosess
	process_id = fork();

	//Tester om fork feilet
	if (process_id < 0) {
		fprintf(stderr, "ERROR: fork failed!\n");
		exit(1);
	}

	//Dreper foreldreprosessen
	if (process_id != 0) {
		fprintf(stderr, "INFO: Process_id of child process %d \n",process_id);
		exit(0);
	}

	//Ignorerer SIGHUP-signal fra prosessgruppeleder
	signal(SIGHUP, SIG_IGN);

	//Gjør prosessen til sesjonsleder og frigjør fra terminal
	sid = setsid();

	if (sid < 0) {
		fprintf(stderr, "ERROR: setsid failed\n");
		exit(1);
	}

	//Oppretter ny barneprosess og avslutter eksisterende
	process_id = fork();
	if (process_id != 0) {
		fprintf(stderr, "INFO: Process_id of child process %d \n", process_id);
		exit(0);
	}

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
}

int privilegeSeparation(int user, int group) { //metode for "privilege-separation", endrer fra root-rettigheter til en annen bruker og gruppe

    uid_t uid = user;
    gid_t gid = group;

    if (getuid() == 0) { //sjekker om man er root
        if (setgid(gid) != 0) { //forsøker å sette group id, avslutter om det feiler
            fprintf(stderr,"ERROR: Unable to change group id and privileges\n");
	    return 1;
        }
        if (setuid(uid) != 0) { //forsøker å sette user id, avslutter om det feiler
            fprintf(stderr,"ERROR: Unable to change user id and privileges\n");
	    return 1;
        }
    }

    else
        fprintf(stderr,"INFO: User not root\n");

    if (setuid(0) != -1) { //sjekker om det er mulig å få tilbake root-tilgang, avlsutter om det er mulig
        fprintf(stderr,"ERROR: Regained root permissions\n exiting...\n");
        return 1;
    }

    fprintf(stderr,"STATUS: Privilege separation complete!\n");
    return 0;
}

int main () { //Web-server

        //demoniserer prosessen slik at denne kjører i bakgrunnen
        daemonizeProcess();

        struct stat *mime_size;
        struct sockaddr_in lok_adr;
        int server_fd, ny_server_fd, err_fd, mime_fd;
        char*mime_types_buffer;

        //Åpner fd til loggfil, dersom filen ikke eksisterer opprettes den
        err_fd = open("var/log/debug.log", O_RDWR | O_CREAT | O_APPEND, S_IRWXU);
        if (-1 == err_fd) {
                fprintf(stderr, "ERROR: Opening or creating debug log file failed..\n");
                exit(1);
        }
        dup2(err_fd, 2); // Dirigerer stderr til errorfil
        close(err_fd);

        //Lager socket
        server_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

        //Hindre at operativsystemet ikke reserverer porten etter http-tjener er ferdig
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &(int){ 1 }, sizeof(int));

        //initierer lokal adresse
        lok_adr.sin_family      = AF_INET;
        lok_adr.sin_port        = htons((u_short)LOKAL_PORT);
        lok_adr.sin_addr.s_addr = htonl(INADDR_ANY);

	//Oppretter fd for mime.types og leser til array
	mime_fd = fd_from_file("etc/mime.types");
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
                fprintf(stderr, "INFO: Process %d is bound to port %d.\n", getpid(), LOKAL_PORT);
        else
		exit(1);

        //Venter på http forespørsel om forbindelse
        listen(server_fd, BAK_LOGG);
        fprintf(stderr, "STATUS: Waiting for client request...\n\n");

	//Endrer rotkatalog til det som skal være web root
	chroot("var/www/");

	//Hvis programmet ikke kjører i container gjennomføres privilege-separasjon for ikke lenger være root. Endrer bruker til hovedbruker (1000:1000)
	if (1 != getppid()) { //tester om foreldreprosess ikke er 1 (noe den vil være når den er initiert med init i en container)
		privilegeSeparation(1000,1000);
	}

	while(1) {

                //Aksepterer mottatt forespørsel
                ny_server_fd = accept(server_fd, NULL, NULL);

                if(0 == fork()) {

			fprintf(stderr, "INFO: New connection, process-id: %d \n", getpid());

			int inc_buf_size = 0;
			char*inc_buf = (char*)malloc(BUF_SIZE),
					*out_buf = (char*)malloc(BUF_SIZE);
			spr_info*request = malloc(sizeof(spr_info));

                        dup2(ny_server_fd, 1); //redirigerer socket tilbake til standard utgang

			inc_buf_size = read(ny_server_fd, inc_buf, BUF_SIZE);

			if (-1 == inc_buf_size) {
				fprintf(stderr, "ERROR: Could not read  ny_server_fd\nterminating\n");
				shutdown(ny_server_fd, SHUT_RDWR);
				exit(1);
			}

			split_request(inc_buf, request); //splitter http-forespørselen og plasserer i struct
			get_file_extension(request); //finner filtype og plasserer i struct
			send_response(ny_server_fd, request, mime_types_buffer); //sender http-respons avhengig av input

                        fflush(stdout); //Sørger for å stenge socket for skriving og lesing
			shutdown(ny_server_fd, SHUT_RDWR);

                        exit(0);
                }

                else {
			signal(SIGCHLD, SIG_IGN);
			close(ny_server_fd);
                }
        }
        return 0;
}
