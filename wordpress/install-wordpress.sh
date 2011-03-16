#!/bin/bash
CURRENT_IP=$(ifconfig eth0|sed -n '/inet addr/ { s/.*inet addr://;s/ .*//;p }')
export DEBIAN_FRONTEND=noninteractive

SOUT="/tmp/wordpress-${USER}.log"
EOUT="/tmp/wordpress-${USER}-error.log"
echo > ${SOUT}
echo > ${EOUT}

if [[ ! -x /usr/sbin/ufw ]];then
    echo -n "Installing firewall: "
    sudo apt-get -y install ufw >>${SOUT} 2>${EOUT}
    sudo ufw allow proto tcp from any to any port 22 >>${SOUT} 2>${EOUT}
    sudo ufw -f enable >>${SOUT} 2>${EOUT}
    echo "done."
fi

echo -n "Installing web/db/wordpress packages (this can be long): "
apt-get -y install vsftpd wordpress php5-curl mysql-server >>${SOUT} 2>${EOUT}
echo "done."

echo -n "Configurating apache: "
a2enmod vhost_alias >>${SOUT} 2>${EOUT}
a2enmod rewrite >>${SOUT} 2>${EOUT}

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


/etc/init.d/apache2 force-reload >>${SOUT} 2>${EOUT}
echo "done."

echo -n "Configuring Database: "
cd /usr/share/doc/wordpress/examples
bash setup-mysql -n wordpress ${CURRENT_IP} >>${SOUT} 2>${EOUT}
echo "done."

echo -n "Configuring Firewall: "
ufw allow 80 >>${SOUT} 2>${EOUT}
echo "done"

echo -n "Adding a demo user: "
useradd -s /bin/bash -m demo 
usermod -G www-data demo
cp -a /root/.ssh /home/demo/
chown -R demo: /home/demo/.ssh
export ROOTPW=$(grep '^root' /etc/shadow|cut -d: -f2) 
sed -i~ "/^demo/ { s/demo:./demo:${ROOTPW/\//\/}/; }" /etc/shadow
echo "Done."

echo -n "Configuring FTP server: "
echo "write_enable=YES" >> /etc/vsftpd.conf
restart vsftpd >>${SOUT} 2>${EOUT}
echo "Done."

echo "Your wordpress can be now accessed from: http://${CURRENT_IP}/"
