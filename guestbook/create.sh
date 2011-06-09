#!/bin/bash
BASEDIR=$(python -c 'import os,sys;print os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[1])))'  $0)
cd ${BASEDIR}
set -e

python python/list-servers.py|egrep -q 'demo-(web1|db1)' && {
    echo "Servers are already created"
    echo "You probably want to do some cleanup before!"
    exit
}

SOUT="/tmp/guestbook-${USER}.log"
EOUT="/tmp/guestbook-${USER}-error.log"

echo "Starting guestbook demo. [Hint] tail ${SOUT} to see
detailled output or ${EOUT} for error log."

echo "----------"

if [[ -e ${BASEDIR}/config ]];then
    source ${BASEDIR}/config
fi

echo > ${SOUT}
echo > ${EOUT}

for name in demo-web1 demo-db1;do
    echo -n "Creating ${name}: "
    python python/create.py -n ${name} -i 69 -f 1 >>${SOUT} 2>${EOUT}
    echo "done."
done

if [[ -z ${DDNS_DOMAIN} || -z ${DDNS_LOGIN} || -z ${DDNS_PASSWORD} ]];then
    echo '${DDNS_DOMAIN} ${DDNS_LOGIN} ${DDNS_PASSWORD} are not defined'
    exit 1
fi
    
echo -n "Getting network Information: "
PUBLIC_WEB_IP=$(./python/info.py -s demo-web1|sed -n '/PublicIP/ { s/.*: //;p}')
PUBLIC_DB_IP=$(./python/info.py -s demo-db1|sed -n '/PublicIP/ { s/.*: //;p}')
PRIVATE_WEB_IP=$(./python/info.py -s demo-web1|sed -n '/PrivateIP/ { s/.*: //;p}')
PRIVATE_DB_IP=$(./python/info.py -s demo-db1|sed -n '/PrivateIP/ { s/.*: //;p}')
echo "done."

ADMIN_DBPASS=$(python ./python/generatepassword.py)
GUESTBOOK_DBPASS=$(python ./python/generatepassword.py)

echo -n "Copying files to webserver: "
scp -q guestbook/scripts/web-setup.sh guestbook/scripts/web-networking.sh root@${PUBLIC_WEB_IP}:
echo "done."
echo -n "Setup webserver: "
ssh -t root@${PUBLIC_WEB_IP} ./web-setup.sh ${GUESTBOOK_DBPASS} ${DDNS_DOMAIN} ${DDNS_LOGIN} ${DDNS_PASSWORD} >>${SOUT} 2>${EOUT}
echo "done."
echo -n "Setup webserver networking: "
ssh -t root@${PUBLIC_WEB_IP} ./web-networking.sh demo-db1 ${PRIVATE_DB_IP} >>${SOUT} 2>${EOUT}
echo "done."

echo -n "Copying files to dbserver: "
scp -q guestbook/scripts/db-setup.sh guestbook/scripts/db-networking.sh root@${PUBLIC_DB_IP}:
echo "done."
echo -n "Setup db: "
ssh -t root@${PUBLIC_DB_IP} ./db-setup.sh ${ADMIN_DBPASS} ${GUESTBOOK_DBPASS} >>${SOUT} 2>${EOUT}
echo "done."
echo -n "Setup db networking: "
ssh -t root@${PUBLIC_DB_IP} ./db-networking.sh demo-web1 ${PRIVATE_WEB_IP} >>${SOUT} 2>${EOUT}
echo "done."

echo "----------"
echo "Guestbook application up and running at http://${DDNS_DOMAIN} or http://${PUBLIC_WEB_IP}"
