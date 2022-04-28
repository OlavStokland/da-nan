#!/bin/bash


if [ $1 = 1 ];then
	./container-init.sh
fi

if [ $1 = 2 ];then
        ./container-restart.sh
fi

if [ $1 = 3 ];then
        ./container-kill.sh
fi
