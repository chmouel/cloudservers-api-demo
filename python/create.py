#!/usr/bin/env python
import os
import sys
from optparse import OptionParser

from lib.common import CNX
from lib.images import Images
from lib.commands import copy_exec_script

BOOTSTRAP = True


def check_image(cnx, server_id):
    import time
    import sys
    toolbar_width = 80

    sys.stdout.write("[%s]" % (" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width + 1))

    while cnx.servers.get(server_id).status != "ACTIVE":
        status = cnx.servers.get(server_id).status
        if status == "ACTIVE":
            break
        elif status == "ERROR":
            print
            print "We have an error while building which is unfortunate" + \
                ", you may have to restart the process again and contact" + \
                " cloud support providing this id: %s" % (server_id)
            sys.exit(1)

        time.sleep(0.5)
        sys.stdout.write("-")
        sys.stdout.flush()

    sys.stdout.write("\n")

opparser = OptionParser(usage="create_vm [container]")
opparser.add_option('-n', '--name',
                    type='str',
                    help="VM Name.")

opparser.add_option('-i', '--id',
                    type='int',
                    help="Image ID.")

opparser.add_option('-f', '--flavor_id',
                    type='int',
                    help="Flavor ID.")

opparser.add_option('-B', '--no-bootstrap',
                    action="store_false",
                    dest="bootstrap",
                    default=BOOTSTRAP,
                    help="No Bootstraping basic configuration")

opparser.add_option('-s', '--script',
                    action="store",
                    dest="script",
                    metavar="FILE",
                    help="Launch this additional file on server after creation")

opparser.add_option('-D', '--delete_image',
                    action="store_true",
                    default=False,
                    help="Delete image from where this is stored after creating")


(options, args) = opparser.parse_args()

if options.script and not os.path.exists(options.script):
    print "%s not exist" % (options.script)
    sys.exit(1)

if options.name:
    IMAGE_NAME = options.name
else:
    ans = raw_input("VM Name: ")
    if not ans.strip():
        print "I need a name. exiting."
        sys.exit(1)
    IMAGE_NAME = ans

if options.id:
    IMAGE_TYPE = options.id
else:
    image = Images(CNX)

    for i in image():
        print "%8s) %s" % (i.id, i.name)
    IMAGE_TYPE = int(raw_input("Choose an Image ID: "))

if options.flavor_id:
    IMAGE_FLAVOUR_ID = options.flavor_id
else:
    for i in CNX.flavors.list():
        print "%s) %s" % (i.id, i.name)
    IMAGE_FLAVOUR_ID = int(raw_input("Choose a Flavor ID: "))

print "Creating Image, please wait...."
cstype = CNX.servers.create(image=IMAGE_TYPE,
                            flavor=IMAGE_FLAVOUR_ID,
                            name=IMAGE_NAME,
                            files={'/root/.ssh/authorized_keys' : open(os.path.expanduser("~/.ssh/id_rsa.pub"), 'r')}
                            )
check_image(CNX, cstype.id)
print "done."

if options.delete_image:
    print "Deleting image of server"
    CNX.images.delete(IMAGE_TYPE)

if options.bootstrap:
    bootstrap_script = os.path.join(os.path.dirname(__file__),
                                    "..", "scripts", "bootstrap.sh")
    copy_exec_script(cstype.public_ip, bootstrap_script)

if options.script:
    copy_exec_script(cstype.public_ip, options.script)

open("/tmp/server-installed-%s.txt" % \
         (os.environ.get("USER", "none")), 'a').write(
    "%s - root@%s -- Password: %s\n" % (cstype.name,
                                        cstype.public_ip,
                                        cstype.adminPass))

if not options.script:
    print
    print
    print "ssh %s -- Password: %s" % (cstype.public_ip, cstype.adminPass)
