#!/usr/bin/python
# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
        
import datetime
import logging
import logging.handlers
import memcache
import os
import re
import sys
import time

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(
                sys.argv[0]),
            "..",
            "python"
            )))

MEMCACHED_SERVERS=["localhost:11211"]

TYPE_NOT_SETUP=-1
TYPE_NOTHING=0
TYPE_START=1
TYPE_END=2
TYPE_ALREADY_CREATED=3
TYPE_NOT_ALREADY_CREATED=4

SERVER_NAMES=['demo-web1', 'demo-db1']
BACKUP_PREFIX="backup"
IMAGE_DEFAULT_FLAVOR_ID=1

class ScheduledTask(object):
    def __init__(self):
        self.mclient = memcache.Client(MEMCACHED_SERVERS, debug=0)
        self.cnx = None

    def setup_log(self, ttype, maxBytes=None, backupCount=7):
        maxBytes = 1024 * 1024 
        date_fmt = '%m/%d/%Y %H:%M:%S'
        log_formatter = logging.Formatter(
            u'[%(asctime)s] %(levelname)-7s: %(message)s )',
            datefmt=date_fmt
            )

        log_name = os.path.join("/tmp/%s.log" % ttype)    

        handler = logging.handlers.RotatingFileHandler(
            log_name,
            maxBytes=maxBytes,
            backupCount=backupCount
            )
        handler.setFormatter(log_formatter)
        handler.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger().addHandler(handler)
        logging.getLogger(__name__).info("Initialized logging subsystem")
        
    def get_cnx(self):
        if not self.cnx:
            from lib.common import CNX
            self.cnx = CNX
            
    def ask_for_time(self, question):
        ask = raw_input(question)
        regexp = re.compile("^(\d+)\s*(minute|second|minute|hour)s?")
        match = regexp.match(ask)
        dt = None

        if match:
            i, t = match.groups()
            if not t.endswith('s'):
                t = t + 's'
            dtn = datetime.datetime.now()
            dt = dtn + datetime.timedelta(**{t : int(i)})
        else:
            if ':' in ask:
                hour, minute = ask.split(':')
            elif 'h' in ask.lower():
                hour, minute = ask.lower().split('h')
            else:
                print "Invalid time format, needs to be in the style of 15:10 or 15h10"
                return
            dtn = datetime.datetime.now()
            dt = datetime.datetime(year=dtn.year,
                                   month=dtn.month,
                                   day=dtn.day,
                                   hour=int(hour),
                                   minute=int(minute))
        return dt

    def is_server_created(self):
        self.get_cnx()
        server_list = self.cnx.servers.list()
        server_list_names = [s.name for s in server_list ]
        lock=False
        for server in SERVER_NAMES:
            if server in server_list_names:
                lock=True
        return lock

    def logAndWait(self, image_id, ftype, ttype):
        previous_status=None

        while True:
            status = ftype.get(image_id).status
            if status != previous_status:
                previous_status = status
                self.mclient.set("demo-cron-%sStatus" % (ttype), status)
            if status == "ACTIVE":
                self.mclient.delete("demo-cron-%sStatus" % (ttype))
                return
            time.sleep(1)
    
    def do_backup(self, delete_server_after=True):
        self.get_cnx()
        server_list = self.cnx.servers.list()
        for server in server_list:
            if server.name in SERVER_NAMES:
                backup_image_name = "%s-%s" % (BACKUP_PREFIX, server.name)
                backuping = self.mclient.get("demo-cron-backupCurrentImage")
                if backuping:
                    print "backup going on exiting"
                    return
                self.mclient.set("demo-cron-backupCurrentImage", server.name)
                self.mclient.set("demo-cron-backupFlavorId%s" % (str(server.name)), server.flavorId)
                backup_image = self.cnx.images.create(backup_image_name, server.id)
                self.logAndWait(backup_image.id, self.cnx.images, "backup")

                self.mclient.delete("demo-cron-backupCurrentImage")
                if delete_server_after:
                    server.delete()

    def exec_cmd(self, public_ip, args):
        from subprocess import Popen, PIPE
        options = [
            'ssh',
            '-q',
            '-t',
            '-o StrictHostKeyChecking=no',
            '-o UserKnownHostsFile=/dev/null'
            ]
        options.append('root@%s' % (public_ip))
        options.extend(args)
        return Popen(options, stdout=PIPE).communicate()[0]
        
    def do_restore(self, delete_image_after=True):
        self.setup_log("restore")
        self.get_cnx()
        images_list = self.cnx.images.list()

        restoring = self.mclient.get("demo-cron-restoreCurrentImage")
        if restoring:
            print "restore going on exiting"
            return
        
        for image in images_list:
            sname = image.name.replace("backup-", "")
            if image.name.startswith("backup-") and sname in SERVER_NAMES:                
                fId = self.mclient.get("demo-cron-backupFlavorId%s" % (str(sname)))
                if fId:
                    fId = int(fId)
                    self.mclient.delete("demo-cron-backupFlavorId%s" % (str(sname)))
                else:
                    fId = IMAGE_DEFAULT_FLAVOR_ID

                self.mclient.set("demo-cron-restoreCurrentImage", sname)                
                cs = self.cnx.servers.create(
                    image=image.id,
                    flavor=fId,
                    name=sname,
                    )

                self.logAndWait(cs.id, self.cnx.servers, "restore")

                if delete_image_after:
                    image.delete()

                if sname == "demo-db1":
                    db_private_ip = cs._info['addresses']['private'][0]
                    db_public_ip = cs._info['addresses']['public'][0]
                elif sname == "demo-web1":
                    web_private_ip = cs._info['addresses']['private'][0]
                    web_public_ip = cs._info['addresses']['public'][0]
                
        if not all([web_private_ip, web_public_ip, db_private_ip, db_public_ip]):
            #TODO: Send mail!
            print "Error while recovering!"
            return

        self.mclient.set("demo-cron-restoreStatus", "ScriptWebNetworking")
        output = self.exec_cmd(web_public_ip, ["./web-networking.sh", "demo-db1", db_private_ip])
        logging.getLogger(__name__).info(output)
        
        self.mclient.set("demo-cron-restoreStatus", "ScriptDBNetworking")
        output = self.exec_cmd(db_public_ip, ["./db-networking.sh", "demo-web1", web_private_ip])
        logging.getLogger(__name__).info(output)

        self.mclient.delete("demo-cron-restoreCurrentImage")
        
    def get_status(self, ttype):
        bCi = self.mclient.get("demo-cron-%sCurrentImage" % (ttype))
        if not bCi:
            print "Nothing going on"
            return
        print "%s:%s" % (self.mclient.get("demo-cron-%sCurrentImage" % (ttype)),
                                       self.mclient.get("demo-cron-%sStatus" % (ttype)))

    def check_if_need_to_run(self, start=None, end=None, now=None):
        if not start:
            mstart=self.mclient.get("demo-cron-start")
            if mstart:
                start = datetime.datetime.fromtimestamp(float(mstart))
            else:
                return TYPE_NOT_SETUP
        if not end:
            mend = self.mclient.get("demo-cron-end")
            if mend:
                end = datetime.datetime.fromtimestamp(float(mend))
            else:
                return TYPE_NOT_SETUP
        if not now:
            now = datetime.datetime.now()

        if now > start and now >= end:
            iscreated = self.is_server_created()
            if not iscreated:
                return TYPE_NOT_ALREADY_CREATED
            return TYPE_END
        elif now >= start:
            iscreated = self.is_server_created()
            if iscreated:
                return TYPE_ALREADY_CREATED
            return TYPE_START
        return TYPE_NOTHING

    def testit(self):
        dtn = datetime.datetime.now()
        now = datetime.datetime(year=dtn.year,
                                month=dtn.month,
                                day=dtn.day,
                                hour=int(14),
                                minute=int(29))

        dtn = datetime.datetime.now()
        start =datetime.datetime(year=dtn.year,
                                 month=dtn.month,
                                 day=dtn.day,
                                 hour=int(14),
                                 minute=int(28))

        end = datetime.datetime(year=dtn.year,
                                month=dtn.month,
                                day=dtn.day,
                                hour=int(14),
                                minute=int(35))
        self.check_if_need_to_run(start=start, end=end, now=now)
            
    def set_cron(self):
        self.help()
        dtn = datetime.datetime.now()

        start_time = self.ask_for_time('Start time: ')
        if dtn  > start_time:
            print "Cannot set a time in the past of this hour"
            return
        self.mclient.set("demo-cron-start", time.mktime(start_time.timetuple()))
        
        end_time = self.ask_for_time('End time: ')
        if start_time > end_time:
            print "End time cannot be before Start time"
            return
        self.mclient.set("demo-cron-end", time.mktime(end_time.timetuple()))
        
    def help(self):
        print """Specify a start and a End time. The format can be :
15h34
15:34
2 minute
5 hours
10 seconds

Please allow at least 10 minutes between start and end time.
"""

if __name__ == '__main__':
    c = ScheduledTask()
    #c.testit()
    #c.set_cron()
    #c.do_backup()
    #c.do_restore()
    #c.get_status("restore")
    #c.get_status("backup")
    # result = c.check_if_need_to_run()
    # if result == TYPE_NOTHING:
    #     print "Nothing to do for today cron."
    # elif result == TYPE_START:
    #     print "I am about to start"
    # elif result == TYPE_END:
    #     print "I am about to end"
    # elif result == TYPE_NOT_SETUP:
    #     print "Nothing is setup."
    # elif result == TYPE_ALREADY_CREATED:
    #     print "You want me to start but servers are already created"
    # elif result == TYPE_NOT_ALREADY_CREATED:
    #     print "You want me to end but servers are not already created"
    
