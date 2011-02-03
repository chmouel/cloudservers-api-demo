#!/bin/bash
cd $(python -c 'import os,sys;print os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[1])))'  $0)

read -e -p "What time do you want to have it backup (format is: 9:00 or 14:50): "
echo $REPLY > /tmp/guestbook-time-backup

read -e -p "What time do you want to have it restore (format is: 9:00 or 14:50): "
echo $REPLY > /tmp/guestbook-time-restore

