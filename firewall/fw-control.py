#!/usr/bin/env python
import sys
import os
from optparse import OptionParser

TOPDIR = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
sys.path.append(os.path.join(TOPDIR, "python"))

from lib.chooseserver import ChooseServer
from lib.common import CNX
from lib.commands import copy_exec_script

usage="""firewall -- simple firewall wrapper to OS firewall wrapper to iptables via the Cloud.

Examples :

firewall allow port XX -- allow only port XX
firewall deny port XX -- disable port XX
firewall disable -- Allow everything!
firewall enable -- Enable firewall.
firewall status -- Show status of firewall."""

if __name__ == '__main__':
    opparser = OptionParser(usage=usage)
    opparser.add_option('-s', '--server',
                        type='string',
                        help="Server List id/name to match")
    (options, args) = opparser.parse_args()    

    c = ChooseServer(CNX)
    if len(c.servers) == 0:
        print "There is no images to process."
        sys.exit(0)
    server_list = c.get_list_of_servers(options.server)
    if not server_list:
        print "No server selected"
        sys.exit(1)

    for server in server_list:
        print "Processing: %s/%s" % (server.name, server.public_ip)
        copy_exec_script(server.public_ip,
                         '%s/firewall/fw-client.sh' % (TOPDIR),
                         args)
        print
