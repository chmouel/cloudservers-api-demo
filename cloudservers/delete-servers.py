#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Chmouel Boudjnah <chmouel@chmouel.com>
import sys

from lib.common import CNX, i_am_about
from lib.chooseserver import ChooseServer

if __name__ == '__main__':
    c = ChooseServer(CNX)
    if len(c.servers) == 0:
        print "There is no servers to process."
        sys.exit(0)

    server_list = c.get_list_of_servers()
    answer = i_am_about("I am about to delete the servers", server_list)

    if answer:
        for x in server_list:
            print "Deleting %s" % (x.name)
            x.delete()
    
