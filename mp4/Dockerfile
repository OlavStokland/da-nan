FROM httpd:alpine AS base_docker

RUN apk update && apk upgrade && apk add nano
RUN apk add --no-cache --upgrade bash

COPY ./myhttp.conf /usr/local/apache2/conf/httpd.conf
