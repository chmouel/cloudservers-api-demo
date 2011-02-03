#!/bin/bash
cd $(python -c 'import os,sys;print os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[1])))'  $0)

if [[ -z $1  ]];then
    echo "I need a type restore or backup"
    exit 1
fi
atype=$1

session_file="/tmp/guestbook-time-${atype}"
[[ -e ${session_file} ]] || exit

time_to_restore=$(cat ${session_file})

chour=$(date '+%k')
chour=${chour#* }
cminute=$(date '+%M')
cminute=$(python -c "import sys;print '%d' % (int(sys.argv[1]))" ${cminute}) #octal

rhour=${time_to_restore/:*}
rhour=$(python -c "import sys;print '%d' % (int(sys.argv[1]))" ${rhour}) #octal

rminute=${time_to_restore#*:}
rminute=$(python -c "import sys;print '%d' % (int(sys.argv[1]))" ${rminute})

if [[ ${chour} == ${rhour} && ${cminute} == ${rminute} ]];then
       ./guestbook/${atype}.sh
fi
