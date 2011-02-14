#!/bin/bash
cd $(python -c 'import os,sys;print os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[1])))'  $0)
set -e

echo "Starting guestbook demo. [Hint] tail /tmp/guestbook.log to see
detailled output or /tmp/guestbook-error.log for error log."

echo "----------"

if [[ -e config ]];then
    source config
fi

echo > /tmp/guestbook.log
echo > /tmp/guestbook-error.log

for name in demo-web1 demo-db1;do
    echo -n "Creating ${name}: "
    python python/create.py -n ${name} -i 69 -f 1 >>/tmp/guestbook.log 2>/tmp/guestbook-error.log
    echo "done."
done

PUBLIC_WEB_IP=$(./python/info.py -s demo-web1|sed -n '/PublicIP/ { s/.*: //;p}')
PUBLIC_DB_IP=$(./python/info.py -s demo-db1|sed -n '/PublicIP/ { s/.*: //;p}')
PRIVATE_WEB_IP=$(./python/info.py -s demo-web1|sed -n '/PrivateIP/ { s/.*: //;p}')
PRIVATE_DB_IP=$(./python/info.py -s demo-db1|sed -n '/PrivateIP/ { s/.*: //;p}')

ADMIN_DBPASS=$(python ./python/generatepassword.py)
GUESTBOOK_DBPASS=$(python ./python/generatepassword.py)

echo -n "Copying files to webserver: "
scp -q guestbook/web-setup.sh guestbook/web-networking.sh root@${PUBLIC_WEB_IP}:
echo "done."
echo -n "Setup webserver: "
ssh -t root@${PUBLIC_WEB_IP} ./web-setup.sh ${GUESTBOOK_DBPASS} >>/tmp/guestbook.log 2>/tmp/guestbook-error.log
echo "done."
echo -n "Setup webserver networking: "
ssh -t root@${PUBLIC_WEB_IP} ./web-networking.sh demo-db1 ${PRIVATE_DB_IP} >>/tmp/guestbook.log 2>/tmp/guestbook-error.log
echo "done."

echo -n "Copying files to dbserver: "
scp -q guestbook/db-setup.sh guestbook/db-networking.sh root@${PUBLIC_DB_IP}:
echo "done."
echo -n "Setup db: "
ssh -t root@${PUBLIC_DB_IP} ./db-setup.sh ${ADMIN_DBPASS} ${GUESTBOOK_DBPASS} >>/tmp/guestbook.log 2>/tmp/guestbook-error.log
echo "done."
echo -n "Setup db networking: "
ssh -t root@${PUBLIC_DB_IP} ./db-networking.sh demo-web1 ${PRIVATE_WEB_IP} >>/tmp/guestbook.log 2>/tmp/guestbook-error.log
echo "done."

echo "----------"
echo "Guestbook application up and running at http://demo-web1.dyndns.info"
