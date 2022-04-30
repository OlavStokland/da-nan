FROM mp4http
# Bruker image fra base_docker Dockerfile som har http:alpine, apache conf fil,
# nano og bin/bash som base. Utenom kravspefikasjon så er det valgtfritt
#hvor du velger og legge til ekstra funksjonalitet.

RUN apk add curl && apk add libxml2-utils && apk add util-linux
#Kopierer cgi script som skal kjøre på container 3
COPY container3/transfer.cgi /usr/local/apache2/cgi-bin/
#COPY container3/html/* /usr/local/apache2/htdocs/
# Setter rettigheter på bruker som skal eksekvere apache2
RUN chown -R www-data:www-data /usr/local/apache2
RUN chmod 755 /usr/local/apache2/cgi-bin/transfer.cgi
# execute cgi script
# kommando for at httpd alltid kjører når container er i live.
CMD ["httpd","-D","FOREGROUND"]
