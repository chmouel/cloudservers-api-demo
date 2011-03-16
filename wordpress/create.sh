#!/bin/bash
cd $(python -c 'import os,sys;print os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[1])))'  $0)
set -e

python python/create.py -i 69 -B -s ./wordpress/install-wordpress.sh

