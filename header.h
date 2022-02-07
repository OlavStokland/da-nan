ẍ#include <arpa/inet.h>
#include <unistd.h> 
#include <stdlib.h>
#include <stdio.h>
#include "stddef.h"
#include "sys/types.h"
#include "sys/stat.h"
#include "fcntl.h"
#include "string.h"


void print_response_to_client(info*, char*);
int fd_from_file(char*);

