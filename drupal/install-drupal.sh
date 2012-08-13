#!/bin/bash
CURRENT_IP=$(ifconfig eth0|sed -n '/inet addr/ { s/.*inet addr://;s/ .*//;p }')
export DEBIAN_FRONTEND=noninteractive

SOUT="/tmp/drupal-${USER}.log"
EOUT="/tmp/drupal-${USER}-error.log"
echo > ${SOUT}
echo > ${EOUT}

if [[ ! -x /usr/sbin/ufw ]];then
    echo -n "Installing firewall: "
    sudo apt-get -y install ufw >>${SOUT} 2>${EOUT}
    sudo ufw allow proto tcp from any to any port 22 >>${SOUT} 2>${EOUT}
    sudo ufw -f enable >>${SOUT} 2>${EOUT}
    echo "done."
fi

apt-get -y update
echo -n "Installing web/db/drupal packages (this can be long): "
apt-get -y install vsftpd drupal6 mysql-server >>${SOUT} 2>${EOUT}
echo "done."

cat <<EOF>/etc/apache2/sites-available/default
<VirtualHost *:80>
   UseCanonicalName    Off
   DocumentRoot /usr/share/drupal6
   Options All
   #ServerAdmin admin@example.com

   Alias /drupal6 /usr/share/drupal6

   <Directory /usr/share/drupal6/>
       Options +FollowSymLinks
       AllowOverride All
       order allow,deny
       allow from all
   </Directory>
</VirtualHost>
EOF

echo -n "Restarting Apache: "
/etc/init.d/apache2 restart >>${SOUT} 2>${EOUT}
echo "done."

echo -n "Configuring Firewall: "
ufw allow 80 >>${SOUT} 2>${EOUT}
echo "done"

echo "Your drupal install can be now finished from: http://${CURRENT_IP}/install.php"

