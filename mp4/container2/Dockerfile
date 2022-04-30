FROM mp4http
# Bruker image fra base_docker Dockerfile som har http:alpine, apache conf fil,
# nano og bin/bash som base. Utenom kravspefikasjon så er det valgtfritt
#hvor du velger og legge til ekstra funksjonalitet.
RUN apk add sqlite && apk add libxml2-utils && apk add util-linux

COPY /container2/api.cgi /usr/local/apache2/cgi-bin/
COPY /container2/diktbase.db /usr/local/apache2/diktbase.db
COPY /container2/diktbase.xsl /usr/local/apache2/htdocs/
#Kopiering av api, database og xsl, stylesheet for xml.

# Endrer rettigheter til at apache2 bruker kan eksekvere filene
RUN chown -R www-data:www-data /usr/local/apache2
#Every user has the right for db.
RUN chmod -R 777 /usr/local/apache2/diktbase.db
#execute on api
RUN chmod 755 /usr/local/apache2/cgi-bin/api.cgi
