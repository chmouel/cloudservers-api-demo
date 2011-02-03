#!/bin/bash
cd $(python -c 'import os,sys;print os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[1])))'  $0)
set -e
echo "Configuring web server 1 and db server 1"

if [[ -e config ]];then
    source config
fi

for name in demo-web1 demo-db1;do
    python cloudservers/create.py -n ${name} -i 69 -f 1
done

WEB_IP=$(python ./cloudservers/list-servers.py | sed -n '/demo-web1/ { s/.*- //;s/ $//;p;}')
DB_IP=$(python ./cloudservers/list-servers.py | sed -n '/demo-db1/ { s/.*- //;s/ $//;p;}')

scp scripts/setup-web-guestbook.sh scripts/adjust-web-networking.sh root@${WEB_IP}:
ssh -t root@${WEB_IP} ./setup-web-guestbook.sh
ssh -t root@${WEB_IP} ./adjust-web-networking.sh demo-db1 ${DB_IP}

scp scripts/setup-db.sh scripts/adjust-db-networking.sh root@${DB_IP}:
ssh -t root@${DB_IP} ./setup-db.sh
ssh -t root@${DB_IP} ./adjust-db-networking.sh demo-web1 ${WEB_IP}

