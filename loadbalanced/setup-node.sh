#!/bin/bash
LOADBALANCER_IP=$1

if grep -q '^10.*loadbalancer.local$' /etc/hosts;then
    sed "/^10.*loadbalancer.local$/ { s/^[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*/$LOADBALANCER_IP/ }" /etc/hosts
else
    cat<<EOF>>/etc/hosts

${LOADBALANCER_IP} loadbalancer.local
EOF
fi

apt-get -y install python-memcache libapache2-mod-php5 php5-curl

ufw allow from ${LOADBALANCER_IP}

a2enmod php5 
service apache2 restart

rm -f /var/www/index.html

mkdir -p /usr/share/php
cd /usr/share/php
git clone git://github.com/rackspace/php-cloudfiles.git

cat <<EOF>/etc/cron.d/store-loadavg
*/5 *     * * *     root   /usr/local/bin/store-load-avg.py
EOF
