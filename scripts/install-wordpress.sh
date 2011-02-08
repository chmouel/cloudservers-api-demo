#!/bin/bash
CURRENT_IP=$(ifconfig eth0|sed -n '/inet addr/ { s/.*inet addr://;s/ .*//;p }')
export DEBIAN_FRONTEND=noninteractive
apt-get -y install wordpress mysql-server

a2enmod vhost_alias
a2enmod rewrite

cat <<EOF>/etc/apache2/sites-available/default
    <VirtualHost *:80>
    UseCanonicalName    Off
    VirtualDocumentRoot /var/www/%0
    Options All
    #ServerAdmin admin@example.com

    # Store uploads in /var/www/wp-uploads/\$0
    RewriteEngine On
    RewriteRule ^/wp-uploads/(.*)$ /var/www/wp-uploads/%{HTTP_HOST}/\$1

    </VirtualHost>
EOF

ln -s /usr/share/wordpress /var/www/$CURRENT_IP


/etc/init.d/apache2 force-reload

cd /usr/share/doc/wordpress/examples
bash setup-mysql -n wordpress ${CURRENT_IP}

ufw allow 80
