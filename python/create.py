#!/usr/bin/env python
import os
import sys
from subprocess import call
from optparse import OptionParser

from lib.common import CNX
from lib.images import Images

bootstrap=True

def check_image(cnx, server_id):
    import time
    import sys
    toolbar_width = 80

    sys.stdout.write("[%s]" % (" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

    while cnx.servers.get(server_id).status != "ACTIVE":
        status=cnx.servers.get(server_id).status
        if status  == "ACTIVE":
            break
        elif status == "ERROR":
            print
            print "We have an error while building which is unfortunate, you may have to restart the process again and contact cloud support providing this id: %s"  % (server_id)
            sys.exit(1)
            
        time.sleep(0.5) # do real work here
        sys.stdout.write("-")
        sys.stdout.flush()

    sys.stdout.write("\n")

opparser = OptionParser(usage="create_vm [container]")
opparser.add_option('-n', '--name',
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
                    default=True,
                    help="No Bootstraping basic configuration")

opparser.add_option('-D', '--delete_image',
                    action="store_true",
                    default=False,
                    help="Delete image from where this is stored after creating")


(options, args) = opparser.parse_args() # pylint: disable-msg=W0612

if options.name:
    IMAGE_NAME=options.name
else:
    ans = raw_input("VM Name: ")
    if not ans.strip():
      print "I need a name. exiting."
      sys.exit(1)
    IMAGE_NAME=ans

if options.id:
    IMAGE_TYPE=options.id
else:
    image = Images(CNX)

    for i in image():
        print "%8s) %s" % (i.id, i.name)
    IMAGE_TYPE = int(raw_input("Choose an Image ID: "))

if options.flavor_id:
    IMAGE_FLAVOUR_ID=options.flavor_id
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
    public_ip=cstype.public_ip
    ssh_options = ['-q', '-t', '-o StrictHostKeyChecking=no', '-o UserKnownHostsFile=/dev/null']
    call('ssh %s root@%s "sudo apt-get -y install curl  && curl http://www.chmouel.com/pub/bootstrap.sh|sh -"' % (" ".join(ssh_options), public_ip), shell=True)

open("/tmp/server-installed.txt", 'a').write("%s - root@%s -- Password: %s\n" % (cstype.name, cstype.public_ip, cstype.adminPass))
print
print
print "ssh %s -- Password: %s" % ( cstype.public_ip, cstype.adminPass)