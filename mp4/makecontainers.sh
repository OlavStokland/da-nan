#!/bin/bash

rm container2/diktbase.db
sqlite3 container2/diktbase.db < opprett_database.sql

# fjerner tidligere instanser av docker images og containere

docker kill api;
docker kill web;

docker rm api;
docker rm web;

#remove and untag. da er vi sikre på at det starter fresht.

docker rmi api;
docker rmi web;

# lager egen cpu gruppe for at containere blir limtert til den gruppen

echo "old instance removed, initiating new one ."

sudo systemctl stop docker
sudo dockerd docker daemon --userns-remap=default &
sudo systemctl start docker

# bygger 3 kontainere basert på docker filen
docker build -f Dockerfile . -t mp4http --target base_docker
docker build -f container2/Dockerfile . -t api
docker build -f container3/Dockerfile . -t web

# kjører opp containere, med, capabilities og namespaces
# -d for kjøre i bakgrunnen

docker run -d  --userns=dockremap --cap-drop=all \
 --cap-add=CHOWN --cap-add=AUDIT_WRITE --cap-add=DAC_OVERRIDE \
 --cap-add=KILL --cap-add=NET_RAW --cap-add=NET_BIND_SERVICE \
 --cpu-shares 512 --pids-limit 200 --memory 512m \
 --net=bridge --name api -p 8081:80 api

docker run -d --cap-drop=all \
 --cap-add=CHOWN --cap-add=AUDIT_WRITE --cap-add=DAC_OVERRIDE \
 --cap-add=KILL --cap-add=NET_RAW --cap-add=NET_BIND_SERVICE \
 --cpu-shares 512 --pids-limit 200 --memory 512m \
 --net=bridge --name web -p 8082:80 web
