#!/bin/bash
LOCAL='/opt/tap/nextgen/temp/tapin'
REMOTE='/rocra_polled/Polled/tapin'

ftp -in 10.195.3.131 <<FTP_CMD
user mtnftp mtnftp
lcd $LOCAL
cd $REMOTE
bin
mput CD*
bye
FTP_CMD

if [[ $? -eq 0 ]];then
   exit 0
else
   exit 1
fi
