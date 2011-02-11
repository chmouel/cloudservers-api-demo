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

        scp ${mydir}/store-load-avg.py ${mydir}/setup-node.sh root@${ip}:/usr/local/bin/
        scp ${mydir}/tmp/config.php root@${ip}:/etc/apidemo-config.php
        
        ssh -t root@${ip} "/usr/local/bin/setup-node.sh" ${PRIVATE_LOADBALANCER_IP}

        scp ${mydir}/CF_Cached.php root@${ip}:/var/www/index.php
    done
}

function setup_loadbalancer() {
    scp ${mydir}/setup-loadbalancer.sh ${mydir}/rscloud.py ${mydir}/dynamic-host.py root@${LOADBALANCER_IP}:/usr/local/bin/
    ssh -t root@${LOADBALANCER_IP} "/usr/local/bin/setup-loadbalancer.sh ${USER} ${API_KEY} ${AURL}"
}

function save_first_image() {
    ./python/backup.py -s loadbalanced1 -f -b "saved-"
}

function create_servers() {
   ./python/create.py -n loadbalancer.rackspace.co.uk -f 1 -i 69
    c=1
    while true;do
        ./python/create.py -n loadbalanced${c}.rackspace.co.uk -f 1 -i 69;
        [[ $c == ${NUM_NODES} ]] && break
        (( c++ ))
    done
}

prepare_config_php_file
create_servers
setup_nodes
save_first_image
setup_loadbalancer
