#!/bin/bash
mydir=$(python -c 'import os,sys;print os.path.dirname(os.path.realpath(sys.argv[1])) ' $0)
cd $(python -c 'import os,sys;print os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[1])))'  $0)
set -e

###CONFIGURATION
CONTAINER="public"
OBJECT="apidemo.html"
NUM_NODES=2
CACHE_TIME=10
##########

function prepare_config_php_file() {
    if [[ ${RCLOUD_DATACENTER} == "us" || ${RCLOUD_DATACENTER} == "US" ]];then
        PHPAUTHSERVER="US_AUTHURL"
        AURL=$US_RCLOUD_AURL
        USER=$US_RCLOUD_USER
        API_KEY=$US_RCLOUD_KEY
    else
        PHPAUTHSERVER="UK_AUTHURL"
        AURL=$UK_RCLOUD_AURL
        USER=$UK_RCLOUD_USER
        API_KEY=$UK_RCLOUD_KEY
    fi
    
    cat <<EOF>${mydir}/tmp/config.php
<?php
\$FILE="/var/tmp/index.html";
\$CONTAINER="${CONTAINER}";
\$OBJECT="${OBJECT}";
\$AUTH_SERVER=${PHPAUTHSERVER};
\$USER="${USER}";
\$API_KEY="${API_KEY}";
\$CACHE_TIME="${CACHE_TIME}";
?>
EOF
}

function setup_nodes() {
    PRIVATE_LOADBALANCER_IP=$(python python/info.py -s loadbalancer -f PrivateIP|cut -d":" -f3)
    
    for line in $(python python/info.py -s  loadbalance -f PublicIP|sort -r);do
        _ipnum=${line%:*}
        ipnum=${_ipnum##*:}
        if [[ ${ipnum} != 1 ]];then
            continue
        fi
        ip=${line##*:}
        _name=${line%%:*}
        name=${line%%.*}

        if [[ ${name} == loadbalancer* ]];then
            LOADBALANCER_IP=${ip}
            continue
        fi

        echo -n "Copying files to ${name}: "
        scp -q ${mydir}/store-load-avg.py ${mydir}/setup-node.sh root@${ip}:/usr/local/bin/
        scp -q ${mydir}/tmp/config.php root@${ip}:/etc/apidemo-config.php
        echo "done."
        
        echo -n "Starting setup for ${name}: "
        ssh -q -t root@${ip} "/usr/local/bin/setup-node.sh" ${PRIVATE_LOADBALANCER_IP} >>/tmp/log 2>/tmp/error
        echo "done."

        echo -n "Copying cloudfiles wrapper to ${name}: "
        scp -q ${mydir}/CF_Cached.php root@${ip}:/var/www/index.php
        echo "done."
    done
}

function setup_loadbalancer() {
    echo -n "Copying files to loadbalancer: "
    scp -q ${mydir}/setup-loadbalancer.sh ${mydir}/rscloud.py ${mydir}/dynamic-host.py root@${LOADBALANCER_IP}:/usr/local/bin/
    echo "done."

    echo -n "Setting up loadbalancer: "
    ssh -t root@${LOADBALANCER_IP} "/usr/local/bin/setup-loadbalancer.sh ${USER} ${API_KEY} ${AURL}" >>/tmp/log 2>/tmp/error
    echo "done."
}

function save_first_image() {
    echo -n "Backuping as image loadbalanced1: "
    ./python/backup.py -s loadbalanced1 -f -b "saved" >>/tmp/log 2>/tmp/error
    echo "done."
}

function create_servers() {
    echo -n "Creating loadbalancer: "
    ./python/create.py -n loadbalancer.rackspace.co.uk -f 1 -i 69 >>/tmp/log 2>/tmp/error
    echo "done."
    c=1
    while true;do
        echo -n "Creating loadbalanced${c}: "
        ./python/create.py -n loadbalanced${c}.rackspace.co.uk -f 1 -i 69 >>/tmp/log 2>/tmp/error
        echo " done."
        [[ $c == ${NUM_NODES} ]] && break
        (( c++ ))
    done
}

echo -n "Preparing file configuration: "
prepare_config_php_file
echo "done."
create_servers
setup_nodes
save_first_image
setup_loadbalancer
