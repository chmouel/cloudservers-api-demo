#!/bin/bash
cd $(python -c 'import os,sys;print os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[1])))'  $0)
set -e
echo "Creating and configuring web server 1 and db server 1"
echo "This may take a (litle, this is still the cloud) while enjoy the matrix output and relax!"

if [[ -e config ]];then
    source config
fi

for name in demo-web1 demo-db1;do
    python python/create.py -n ${name} -i 69 -f 1
done

WEB_IP=$(python ./python/list-servers.py | sed -n '/demo-web1/ { s/.*- //;s/ $//;p;}')
DB_IP=$(python ./python/list-servers.py | sed -n '/demo-db1/ { s/.*- //;s/ $//;p;}')

ADMIN_DBPASS=$(python ./python/generatepassword.py)
GUESTBOOK_DBPASS=$(python ./python/generatepassword.py)

scp scripts/setup-web-guestbook.sh scripts/adjust-web-networking.sh root@${WEB_IP}:
ssh -t root@${WEB_IP} ./setup-web-guestbook.sh ${GUESTBOOK_DBPASS}
ssh -t root@${WEB_IP} ./adjust-web-networking.sh demo-db1 ${DB_IP}

scp scripts/setup-db.sh scripts/adjust-db-networking.sh root@${DB_IP}:
ssh -t root@${DB_IP} ./setup-db.sh ${ADMIN_DBPASS} ${GUESTBOOK_DBPASS}
ssh -t root@${DB_IP} ./adjust-db-networking.sh demo-web1 ${WEB_IP}

