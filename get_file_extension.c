#include "header.h"

/* 0 = ingen fil, redirect
   -1 = ingen filendelse, bad request
   1  =  funnet filendelse, lagt i request->url_exstension
*/
int get_file_extension(spr_info*request) {

	if(!strcmp(request->url, "/")) //Hvis forespørsel innholder bare / så er det ingen fil. aka f.eks ingen text.txt og referere til. 
		return 0; 


	// VI tar med filendelsen
	request->url_extension = strrchr(request->url, '/'); //finner siste forekomst av /
	request->url_extension = strrchr(request->url_extension, '.'); //her finner vi hvis det er en fil, feks text.txt


	
