#!/bin/bash
#TODO: Networking
GUESTBOOK_DBPASS=$1

if [[ -z ${GUESTBOOK_DBPASS} ]];then
    GUESTBOOK_DBPASS="blaha331002"
fi

set -e
export DEBIAN_FRONTEND=noninteractive
aptitude -y install ufw lighttpd php5-cgi php5-mysql unzip mysql-client ddclient

cat <<EOF>~/.my.cnf
[client]
user = guestbook
database = guestbook
password = ${GUESTBOOK_DBPASS}
host = demo-db1
EOF

cd /tmp
wget -c -O/tmp/j.zip -c http://jibberbook.googlecode.com/files/jibberbook-2.3.zip
unzip j.zip
mv jibberbook-2.3/* /var/www

rm -rf jibberbook-2.3/

cd /var/www
rm -f index.lighttpd.html
chown www-data: data_layer/xml/comments.xml

sed -i -n '/JB_STORAGE/ { s/xml/mysql/ };/JB_PASSWORD/ { s/password/russell/ }; /JB_MYSQL/d; p' inc/config.php
cat <<EOF>>inc/config.php
<?php
define('JB_MYSQL_HOST', 'demo-db1');
define('JB_MYSQL_USERNAME', 'guestbook');
define('JB_MYSQL_PASSWORD', '${GUESTBOOK_DBPASS}');
define('JB_MYSQL_DATABASE', 'guestbook');
define('JB_MYSQL_TABLE', 'gbtable');
?>
EOF

for i in fastcgi fastcgi-php;do
    lighty-enable-mod $i
done
/etc/init.d/lighttpd force-reload

cat <<EOF>/etc/ddclient.conf
# Configuration file for ddclient generated by debconf
#
# /etc/ddclient.conf

protocol=dyndns2
use=web, web=checkip.dyndns.com, web-skip='IP Address'
server=members.dyndns.org
login=chmouelrack
password='rackspace'
demo-web1.dyndns.info

EOF
/etc/init.d/ddclient start
