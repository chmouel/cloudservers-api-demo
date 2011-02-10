#!/usr/bin/env python
# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
import sys

from lib.common import CNX
from lib.chooseserver import ChooseServer
from optparse import OptionParser

def parse_options():
    opparser = OptionParser(usage="detailled-infos.py")

    opparser.add_option('-s', '--server',
                        type='string',
                        help="Server List id/name to match")

    opparser.add_option('-f', '--filter',
                    type='string',
                    action="store",
                    metavar="FILTER",
                    dest="filter",
                    help="Filter only by PublicIP, PrivateIP, FlavorID")

    (options, args) = opparser.parse_args() # pylint: disable-msg=W0612
    return options

def print_net(t, dico, label=None):
    cnt=1
    for ip in dico[t]:

        if label:
            plabel="%s:%d:" % (label, cnt)
        else:
            if cnt == 1:
                plabel="%sIP: " % (t.capitalize())
            else:
                plabel="%sIP%d: " % (t.capitalize(), cnt)
        print "%s%s" % (plabel, ip)
        cnt+=1

def main():
    c = ChooseServer(CNX)
    options = parse_options()
    server_list = c.get_list_of_servers(options.server)

    if not server_list:
        sys.exit(1)

    i = 1
    for server in server_list:
        info = server._info

        if options.filter:
            if options.filter == "PublicIP":
                print_net("public", info['addresses'], label="%s" % (server.name))
                continue
            
            if options.filter == "PrivateIP":
                print_net("private", info['addresses'], label="%s" % (server.name))
                continue

        print "Name: %s" % (server.name)
        print_net("public", info['addresses'])
        print_net("private", info['addresses'])
        print "ID: %d" % (info['id'])
        print "Host ID: %s" % (info['hostId'])
        print "Flavor ID: %s" % (info['flavorId'])
        #print "Backup: %s" % (server.backup_schedule.enabled)
        m = info['metadata']
        if m:
            print "Metadata: %s" % (m)

        if len(server_list) != i:
            print
        i+=1
        
if __name__ == '__main__':
    main()
