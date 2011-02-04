Introduction
============

This is a couple of scripts that show up how the RackSpace Cloud
Servers API works. It is by design keep simple to be easy to peek or
to look at.

REQUIREMENT
==========

These demos needs the python-cloudservers library, unfortunately the
upstream version from here :

http://packages.python.org/python-cloudservers/

Doesn't support different auth server, so the easiest way is to download
my forked version :

https://github.com/chmouel/python-cloudservers/tarball/master

and install it in your PYTHONPATH (usually
/usr/local/lib/python${PYTHON_VERSION}/site-packages/ )

CONFIGURATION
=============

You would need to have a file config in the root directory of this
software containing information about your Cloud containing :

    export RCLOUD_DATACENTER="UK"

    export US_RCLOUD_USER=""
    export US_RCLOUD_KEY=""
    export US_RCLOUD_AURL="https://auth.api.rackspacecloud.com/v1.0"

    export UK_RCLOUD_USER=""
    export UK_RCLOUD_KEY=""
    export UK_RCLOUD_AURL="https://lon.auth.api.rackspacecloud.com/v1.0"

You don't have to have two different account but make sure
RCLOUD_DATACENTER goes to the right ones.

SCRIPTS
=======

The python directory has all the python scripts which is the guts to
interact with cloudservers.

This is the description of what the script does :

 * backup.py
   
   Allow you to choose a image to backup into RackSpace Cloud Files
   (by default on RackSpace UK Cloud).

 * create.py
 
   Will ask you to create a new image into the cloud and will launch a
   script on it with some basic configurations.

 * delete-images.py
 
   Give you the opportunity to delete your stored images (or backups).

 * delete-servers.py
 
   Give you the opportunity to delete your stored servers.
   
 * generatepassword.py

   A simple script that output a nice generated random password (human
   readable).

 * list-images.py
 
   Will list your images available (not the system ones only yours).

 * list-servers.py

   Will list your servers in your cloud.
  
APPLICATIONS
===========

Applications are different roles for showcasing the demos. As a start
we have the guestbook application which create two servers a WEB and
DB install a guestbook apps on it configure and secure it.

The purpose of this demo is to have it to setup a periodic task (cron)
to backup the VM  at certain time and automatically start it again at
another time.

In the guestbook directory we have :

  * create.sh

    Will create a web and a db server copy your SSH id_rsa key
    ~/.ssh/id_rsa for SSH access and launch the scripts
    setup-web-guestbook.sh and setup-db.sh from your scripts
    directory. And configure neworking with the adjust-db-networking.sh
    and adjust-web-networking.sh

  * backup.sh

    Would backup those images in the cloud and deleting the server

  * restore.sh

    Would backup the images and adjust the networking on the server
    with the adjust-db or web networking scripts.

  * cron.sh

    This is the cron that takes care to check the files
    /tmp/guestbook-files-backup or /tmo/guestbook-files-restore for
    the time when the backup.sh and restore.sh needs to be
    started. You would need to configure your cron to launch it like
    this entry :

    */1 * * * * /home/russell/api-demo/guestbook/cron.sh backup &>/tmp/backup-log.txt
    */1 * * * * /home/russell/api-demo/guestbook/cron.sh restore &>/tmp/restore-log.txt

  * setup-cron.sh

    Simple script that ask you for the time to backup and restore and
    dump the time in the /tmp/guestbook-file-{restore,backup}


  
    

 
