#!/bin/bash
export DEBIAN_FRONTEND=noninteractive

SETUP=
if [[ -f /etc/redhat-release ]];then
    DISTRO="redhat"
    if [[ ! -x /usr/bin/system-config-securitylevel-tui ]];then
        yum -y install system-config-securitylevel-tui
    fi
elif [[ -x /usr/bin/lsb_release ]];then
    DISTRO=$(lsb_release -i -s)
    [[ ${DISTRO,,} == "ubuntu" ]] && DISTRO="debian"

    if [[ ${DISTRO,,} == "debian" && ! -x /usr/sbin/ufw ]];then
        apt-get -y install ufw
    fi

    SETUP="1"
fi

if [[ $1 == "status" ]];then
    if [[ ${DISTRO} == "debian" ]];then
        ufw status numbered
    elif [[ ${DISTRO} == "redhat" ]];then
        iptables -L -n
    fi
    exit
elif [[ $1 == disable ]];then
    if [[ ${DISTRO} == "debian" ]];then
        ufw -f disable
    elif [[ ${DISTRO} == "redhat" ]];then
        echo -n "Disabling firewall: "
        system-config-securitylevel-tui  --disabled -q
        echo "done."
    fi
    exit 0
elif [[ $1 == enable ]];then
    if [[ ${DISTRO} == "debian" ]];then
        ufw allow proto tcp from any to any port 22
        ufw -f enable
    elif [[ ${DISTRO} == "redhat" ]];then
        echo -n "Enabling firewall: "
        system-config-securitylevel-tui  --enabled -q
        echo "done."
    fi
    exit 0
elif [[ $@ == allow\ port* ]];then
    PORT=${@: -1}
    if [[ ${DISTRO} == "debian" ]];then
        ufw allow ${PORT}
    elif [[ ${DISTRO} == "redhat" ]];then
        system-config-securitylevel-tui  -p ${PORT}:tcp -q
        echo "Rules added"
    fi
    exit
elif [[ $@ == deny\ port* ]];then
    PORT=${@: -1}
    if [[ ${DISTRO} == "debian" ]];then
        ufw deny ${PORT}
    elif [[ ${DISTRO} == "redhat" ]];then
        sed -i  "/^-A RH-Firewall.*dport ${PORT} -j ACCEPT/d" /etc/sysconfig/iptables 
        iptables-restore < /etc/sysconfig/iptables
        echo "Rules deleted"
    fi
    exit
else
    if [[ ${DISTRO} == "debian" ]];then
        if [[ -z $@ ]];then
            ufw help
        else
            ufw $@
        fi
    elif [[ ${DISTRO} == "redhat" ]];then
        if [[ -z $@ ]];then
            echo "I am about to launch the GUI to configure the server"
            system-config-securitylevel-tui
        else
            system-config-securitylevel-tui $@
        fi
    fi
fi
