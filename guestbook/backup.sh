#!/bin/bash
cd $(python -c 'import os,sys;print os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[1])))'  $0)

if [[ -e config ]];then
    source config
fi

TEMP_FILE=/tmp/gestbook-backup-lock.txt

function clean_up {
	rm -f $TEMP_FILE
	exit
}

trap clean_up SIGHUP SIGINT SIGTERM

if [[ -e ${TEMP_FILE} ]];then
    exit 120
fi
touch ${TEMP_FILE}

WEB_IP=$(python ./cloudservers/list-servers.py | sed -n '/demo-web1/ { s/.*- //;s/ $//;p;}')
DB_IP=$(python ./cloudservers/list-servers.py | sed -n '/demo-db1/ { s/.*- //;s/ $//;p;}')

[[ -z ${WEB_IP} ]] && clean_up

./cloudservers/backup.py -s "demo-web1 demo-db1" -f -D -b backupprefix

rm -f ${TEMP_FILE}


