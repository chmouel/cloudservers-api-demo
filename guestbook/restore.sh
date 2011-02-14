#!/bin/bash
cd $(python -c 'import os,sys;print os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[1])))'  $0)

if [[ -e config ]];then
    source config
fi

TEMP_FILE=/tmp/guestbook-restore-lock.txt

function clean_up {
	rm -f $TEMP_FILE
	exit
}

trap clean_up SIGHUP SIGINT SIGTERM

if [[ -e ${TEMP_FILE} ]];then
    exit 120
fi
touch ${TEMP_FILE}

WEB_IMAGE_ID=$(python ./python/list-images.py | sed -n '/demo-web1/ { s/-.*//;s/ $//;p;}')
DB_IMAGE_ID=$(python ./python/list-images.py | sed -n '/demo-db1/ { s/-.*//;s/ $//;p;}')

[[ -z ${WEB_IMAGE_ID} || -z ${DB_IMAGE_ID} ]] && clean_up

./python/create.py -B -n demo-web1 -i ${WEB_IMAGE_ID} -f 1 -D  
./python/create.py -B -n demo-db1 -i ${DB_IMAGE_ID} -f 1 -D  

PUBLIC_WEB_IP=$(./python/info.py -s demo-web1|sed -n '/PublicIP/ { s/.*: //;p}')
PUBLIC_DB_IP=$(./python/info.py -s demo-db1|sed -n '/PublicIP/ { s/.*: //;p}')
PRIVATE_WEB_IP=$(./python/info.py -s demo-web1|sed -n '/PrivateIP/ { s/.*: //;p}')
PRIVATE_DB_IP=$(./python/info.py -s demo-db1|sed -n '/PrivateIP/ { s/.*: //;p}')

ssh -t root@${PUBLIC_WEB_IP} ./web-networking.sh demo-db1 ${PRIVATE_DB_IP}
ssh -t root@${PUBLIC_DB_IP} ./db-networking.sh demo-web1 ${PRIVATE_WEB_IP}

rm -f ${TEMP_FILE}

