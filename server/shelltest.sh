#!/bin/bash

res1=`python3.11 -B conf.py 2 1000 1`
check=""
if [ -z "${res1}" ]
then
	echo "error: cannot get server type"
	exit
else
	echo "${res1}.log"
fi

echo "ssssssssssss"

ps -ef | grep "python3.11" | grep -v grep | awk '{print $2}' | xargs kill -9