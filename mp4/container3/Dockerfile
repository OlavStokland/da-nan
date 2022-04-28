FROM mp4http


RUN apk add curl && apk add libxml2-utils && apk add util-linux

COPY container3/transfer.cgi /usr/local/apache2/cgi-bin/
COPY container3/html/* /usr/local/apache2/htdocs/

RUN chown -R www-data:www-data /usr/local/apache2
RUN chmod 755 /usr/local/apache2/cgi-bin/transfer.cgi

CMD ["httpd","-D","FOREGROUND"]
