#!/usr/bin/python
# -*- encoding: utf-8 -*-
import os
import tempfile
import shutil
from rscloud import get_auth, get_servers

def local_name(host):
    return "%s.local" % host.split(".")[0]

def write_fstab(servers):
    fstab_file="/etc/hosts"
    
    fp = open(fstab_file, 'r')
    tmpfile=tempfile.mktemp()
    fw = open(tmpfile, 'w')
    for line in fp:
        if line.startswith("10") and 'loadbalanced' in line:
            continue
        fw.write(line)

    if not line.endswith("\n"):
        fw.write("\n")

    for host in servers:
        if 'loadbalanced' in host:
            fw.write("%s %s\n" % (servers[host], local_name(host)))
    fp.close()
    fw.close()

    shutil.copy(tmpfile, fstab_file)


def write_nginx_lb(servers):
    dest="/etc/nginx/lb.conf"
    fw = open(dest, 'w')
    fw.write("upstream clouddemo {\n")
    for host in servers:
        if 'loadbalanced' in host:
            fw.write("\tserver %s:80;\n" % (local_name(host)))
    fw.write("}\n")
    fw.close()
        
def main():
    auth = get_auth(os.environ["CLOUD_USER"],
                    os.environ["CLOUD_KEY"],
                    os.environ["CLOUD_AUTH_URL"],
                    )
    servers = get_servers(auth)
    lbs={}
    for server in servers:
        lbs[server['name']] = server['addresses']['private'][0]
    write_fstab(lbs)
    write_nginx_lb(lbs)
        
if __name__ == '__main__':
    main()
