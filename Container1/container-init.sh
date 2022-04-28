#!/bin/bash

CONFS=$PWD/container

if [ ! -d $CONFS ];then

	mkdir -p $CONFS/{bin,proc,etc,var/www,var/log}
	cp -r var/www/ $CONFS/var/
	cp /etc/mime.types $CONFS/etc

	gcc --static webserver.c -o $CONFS/bin/webserver.out

	cd       $CONFS/bin/
	cp       /bin/busybox .

	for P in $(./busybox --list | grep -v busybox); do ln busybox $P; done;

	echo "::once:/bin/webserver.out" > $CONFS/etc/inittab

	echo $CONFS
fi

sudo SHELL=/bin/sh PATH=/bin unshare -f -p --mount-proc /usr/sbin/chroot $CONFS bin/init
