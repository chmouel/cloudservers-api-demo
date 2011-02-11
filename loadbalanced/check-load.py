#!/usr/bin/python
import memcache
import os
from rscloud import get_auth, get_servers

MEMCACHED_SERVERS=["127.0.0.1:11211"]

def get_lbs():
    fp = open("/etc/hosts", 'r')
    for line in fp:
        if 'loadbalanced' in line:
            print line[line.find(" "):].strip().replace('.local', '')
            
    fp.close()

def main():
    # auth = get_auth(os.environ["CLOUD_USER"],
    #                 os.environ["CLOUD_KEY"],
    #                 os.environ["CLOUD_AUTH_URL"],
    #                 )
    # servers = get_servers(auth)
    # server_list = [ x['name'] for x in servers if x['name'] == 'loadbalanced']
    mclient = memcache.Client(MEMCACHED_SERVERS, debug=0)

get_lbs()
