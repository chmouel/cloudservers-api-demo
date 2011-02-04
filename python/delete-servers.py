#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from optparse import OptionParser
import sys

from lib.common import CNX, i_am_about
from lib.chooseserver import ChooseServer

if __name__ == '__main__':
    opparser = OptionParser(usage="delete-images")
    opparser.add_option('-s', '--server',
                        type='string',
                        help="Server List id/name to match")
    opparser.add_option('-f', '--force',
                        action="store_true",
                        default=False,
                        help="Force it thought, no question asked.")
    (options, args) = opparser.parse_args() # pylint: disable-msg=W0612
    
    c = ChooseServer(CNX)
    if len(c.servers) == 0:
        print "There is no images to process."
        sys.exit(0)
    server_list = c.get_list_of_servers(options.server)

    if options.force:
        answer=True
    else:
        answer = i_am_about("I am about to delete the images", server_list)
    if answer:
        for x in server_list:
            print "Deleting %s" % (x.name)
            x.delete()

