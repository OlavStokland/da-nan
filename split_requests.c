#include "header.h"
#include "string.h"


void split_requests(char*request_string, spr_info*requests) {

	request->method = strtok(request_string, " "); //splitter opp requesten
	request->url = strtok(NULL, " ");

}


