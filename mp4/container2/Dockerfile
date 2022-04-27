FROM mp4http

RUN apk add sqlite && apk add libxml2-utils && apk add util-linux

COPY /container2/api.cgi /usr/local/apache2/cgi-bin/
COPY /container2/diktbase.db /usr/local/apache2/diktbase.db
COPY /container2/diktbase.xsl /usr/local/apache2/htdocs/

RUN chown -R www-data:www-data /usr/local/apache2
RUN chmod -R 777 /usr/local/apache2/diktbase.db
RUN chmod 755 /usr/local/apache2/cgi-bin/api.cgi
