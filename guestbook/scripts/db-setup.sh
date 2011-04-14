#!/bin/bash
ADMIN_DBPASS=$1
GUESTBOOK_DBPASS=$2

if [[ -z ${ADMIN_DBPASS} ]];then
    ADMIN_DBPASS="randomString33"
fi

if [[ -z ${GUESTBOOK_DBPASS} ]];then
    GUESTBOOK_DBPASS="blaha331002"
fi

export DEBIAN_FRONTEND=noninteractive
apt-get -y install mysql-server ufw 

mysqladmin password ${ADMIN_DBPASS}
cat <<EOF>~/.my.cnf
[client]
password = ${ADMIN_DBPASS}
EOF

BIND_IP=0.0.0.0
PRIVATE_IP=$(ip addr show eth1|sed -n '/^[ ]*inet[ ]/ { s/.*inet //;s/\/.*//;p }')
if [[ ${PRIVATE_IP} == 10.* ]];then
    BIND_IP=${PRIVATE_IP}
fi

sed -i -n "/bind-address/ { s/^/# / };p" /etc/mysql/my.cnf

restart mysql

mysqladmin create guestbook
mysql -e "grant all privileges on guestbook.* to guestbook@'%' identified by '${GUESTBOOK_DBPASS}'"
