#!/bin/bash
# Need latest bash features for =~ and {VARIABLE,,} tricks

cd $(python -c 'import os,sys;print os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[1])))'  $0)
set -e

read -e -p  "How many server to create (max 5): " NUMBER

[[ ${NUMBER} =~ ^[0-9]+$ ]] || { echo "I need you to provide me a number." ; exit 1 ;}

if [[ ${NUMBER} -gt 5 ]];then
    echo "Sorry if we allow too many server to be spawn, Matt would get angry!"
    exit 1
fi

read -e -p "Prefix to use: " PREFIX

[[ -n ${PREFIX} ]] || { echo "I need a prefix!" ; exit 1 ;}

read -e -p "Flavour Type Id (Default: Ubuntu Maverick): " FLAVOUR
[[ -n ${FLAVOUR} ]] || FLAVOUR=69

read -e -p "Image Type Id (Default: Minimal 256m): "  IMAGETYPE
[[ -n ${IMAGETYPE} ]] || IMAGETYPE=1

echo "I am about to create FlavourID ${FLAVOUR}, ImageTypeID ${IMAGETYPE} "
for i in $(seq ${NUMBER});do
    echo -n "${PREFIX}${i} "
done
echo
read -n 2 -e -p "Please confirm by pressing Y or Control-C to abort: " ANSWER
if [[ ${ANSWER,,} != y ]];then
    echo "exiting..."
    exit
fi

for i in $(seq ${NUMBER});do
    name="${PREFIX}${i} "
    echo -n "Creating ${name}: "
    python python/create.py -n ${name} -i 69 -f 1 >>/tmp/create-multi.log 2>/tmp/create-multi-error.log
    echo "done."
done

