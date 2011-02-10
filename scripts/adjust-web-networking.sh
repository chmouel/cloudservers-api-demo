#!/bin/bash
set -e
DBSERVER=$1
DBSERVER_IP=$2

if [[ -z ${DBSERVER} ]];then
    echo "need dbserver name"
    exit 1
fi

if [[ -z ${DBSERVER_IP} ]];then
    echo "Error need a DBSERVER_IP"
    exit 1
fi


if grep -w ${DBSERVER} /etc/hosts;then
    sed -i -n "/${DBSERVER}/ { s/^.*$/${DBSERVER_IP} ${DBSERVER}/};p" /etc/hosts
else
    echo >> /etc/hosts
    echo "${DBSERVER_IP} ${DBSERVER}" >> /etc/hosts
fi

if ! grep -s -w 22 /lib/ufw/user.rules;then
    #first time
    ufw allow proto tcp from any to any port 22
fi

ufw allow 80

/etc/init.d/ddclient restart
