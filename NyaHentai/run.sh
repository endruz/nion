#!/bin/sh
while [ 1 ]; do
    sleep 10
    count=`ps -ef|grep DownloadComics.py|grep -v grep|wc -l`
    echo $count
    if [ "$count" -eq 0 ];then
        echo "start process....."
        nohup python3 DownloadComics.py &
    else
        echo "runing....."
    fi
done