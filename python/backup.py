#!/usr/bin/env python
# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
import time
import sys
from optparse import OptionParser

from lib.common import CNX, i_am_about
from lib.chooseserver import ChooseServer

def wait_for_it(cnx, image_id):
    previous_status=None
    print "Status:"
    while True:
        time.sleep(1)
        status = cnx.images.get(image_id).status
        if status != previous_status:
            previous_status = status
            sys.stdout.write("%s" % (status))
            sys.stdout.flush()
        if status == "ACTIVE":
            print
            return
        sys.stdout.write(".")
        sys.stdout.flush()

def parse_options():
    opparser = OptionParser(usage="backup.py")

    opparser.add_option('-s', '--server',
                        type='string',
                        help="Server List id/name to match")

    opparser.add_option('-f', '--force',
                        action="store_true",
                        default=False,
                        help="Force it thought, no question asked.")


    opparser.add_option('-D', '--delete_after',
                        action="store_true",
                        default=False,
                        help="Delete server after backuping.")

    
    opparser.add_option('-b', '--backup_prefix',
                        type='string',
                        help="Backp prefix of image name")


    (options, args) = opparser.parse_args() # pylint: disable-msg=W0612
    return options

def backup_list_of_servers():
    c = ChooseServer(CNX)
    options = parse_options()

    server_list = c.get_list_of_servers(options.server)

    if not server_list:
        print "no server has been chosen"
        return

    if not options.force:
        answer = i_am_about("Do you want to backup servers [Yn]: ", server_list)

        if not answer or answer.lower() == 'n':
            return

    if options.backup_prefix:
        answer = options.backup_prefix
    else:
        answer = raw_input("Backup prefix [backup]: ")

    if " " in answer:
        print "Spaces are not allowed"
        return
        
    if not answer:
        answer="backup"
    
    for x in server_list:
        backup_name="%s-%s" % (answer, x.name)
        print "Backuping %s to %s: " % (x.name, backup_name)
        b = CNX.images.create(backup_name, x.id)
        wait_for_it(CNX, b.id)
        if options.delete_after:
            print "Deleting: %s" % x.name
            x.delete()
        
if __name__ == '__main__':
    backup_list_of_servers()
