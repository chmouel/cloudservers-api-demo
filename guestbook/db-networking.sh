#!/bin/bash
set -e
WEBSERVER=$1
WEBSERVER_IP=$2

if [[ -z ${WEBSERVER} ]];then
    echo "need webserver name"
    exit 1
fi

if [[ -z ${WEBSERVER_IP} ]];then
    echo "Error need a WEBSERVER_IP"
    exit 1
fi


if grep -w ${WEBSERVER} /etc/hosts;then
    sed -i -n "/${WEBSERVER}/ { s/^.*$/${WEBSERVER_IP} ${WEBSERVER}/};p" /etc/hosts
else
    echo >> /etc/hosts
    echo "${WEBSERVER_IP} ${WEBSERVER}" >> /etc/hosts
fi

ufw disable
if ! grep -s -w 22 /lib/ufw/user.rules;then
    #first time
    ufw allow proto tcp from any to any port 22
else
    sed -i '/3306/d' /lib/ufw/user.rules
fi
ufw allow proto tcp from ${WEBSERVER_IP} to any port 3306
ufw --force enable

restart mysql

#/etc/init.d/ddclient restart
