#include "header.h"
#include "sys/stat.h"
#include "sys/types.h"
#include "unistd.h"



//Error handling
void func_error(char*error_msg, int error_code) {
	printf("HTTP/1.1 %d Not Found\n", error_code);
	printf("Content-Type: plain/text; charset=UTF-8\n");
	printf("Connection: Closed\n");
	printf("\n");
	printf("%d: %s\n", error_code, error_msg);
}

void func_wrap(int size_of_content, char*body, spr_info*request) {
	printf("HTTP/1.1 200 OK\n");
	printf("Content-Type: %s; charset=UTF-8\n", request->content_type);
	printf("Connection: Closed\n");
	printf("Content-Length: %d;\n", size_of_content);
	printf("\n");
	printf("%s\n", body);
}


//les filen
char*file_reader(char*file_path) {
	struct stat*file = malloc(sizeof(struct stat));
	int respons;
	char*buffer;

	respons = fd_from_file(file_path);
	fstat(respons, file);
	buffer = (char*) malloc(file->st_size+1);

	if (-1 == read(respons, buffer, file->st_size))
		fprintf(stderr, "ERROR: kunne ikke lese: %s\n", file_path);
	strcat(buffer, "\0");

	close(respons);
	free(file);

	return buffer;
}


void print_response_to_client(spr_info*request, char*mime_types_buffer) {

	char*buffer;
	int respons = 0, match = 0;


	// Det er en verdi i url_extension
	if (request->url_extension) {

		// kanskje den printer ut asis filen
		if (!strcmp("asis", request->url_extension+1)) {
			printf("%s", file_reader(request->url));
			return;
		}

		// finnes i mimetypes: returnerer 1
		match = req_clearance(request, mime_types_buffer);

		// Det er IKKE match - filtypen IKKE kan aksepteres
		// da eksisterer ikke objektet - 404
		if (match == 0) {
			func_error("Filtypen støttes ikke", 415);
		}

		// Det er match - filtypen kan aksepteres
		else if (match == 1) {
			respons = fd_from_file(request->url);
			if (-1 == respons) {
				fprintf(stderr, "ERROR: Ikke lesetilgang, eller ikke funnet");
				func_error("Filtypen støttes, men finner ikke fil", 404);
			}
			else {
				buffer = file_reader(request->url);
				func_wrap(strlen(buffer)+1, buffer, request);
				free(buffer);
			}
			close(respons);
		}
	}

	else if (request->url && !request->url_extension)
		func_error("filentypen støttes ikke", 404);

	// Ingen objekter etterspørres - rediriger
	else if (!request->url) {
		buffer = file_reader("index.html");
		func_wrap(strlen(buffer)+1, buffer, request);
		free(buffer);
	}
}
