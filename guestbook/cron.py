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
import optparse

SET_CRON_HELP = """Specify a start and a End time. The format can be :
15h34
15:34
2 minute
5 hours
10 seconds

Please allow at least 10 minutes between start and end time.
"""

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(
                sys.argv[0]),
            "..",
            "python")))

MEMCACHED_SERVERS = ["localhost:11211"]

TYPE_NOT_SETUP = -1
TYPE_NOTHING = 0

TYPE_BACKUP = 1
TYPE_RECOVER = 2
TYPE_CANNOT_BACKUP = 3
TYPE_CANNOT_RECOVER = 4

SERVER_NAMES = ['demo-web1', 'demo-db1']
BACKUP_PREFIX = "backup"
IMAGE_DEFAULT_FLAVOR_ID = 1


def timesince(d, now=None):
    def ppr(s, p, n):
        if n == 1:
            return s
        return p
    chunks = (
      (60 * 60 * 24 * 365, lambda n: ppr('year', 'years', n)),
      (60 * 60 * 24 * 30, lambda n: ppr('month', 'months', n)),
      (60 * 60 * 24, lambda n: ppr('day', 'days', n)),
      (60 * 60, lambda n: ppr('hour', 'hours', n)),
      (60, lambda n: ppr('minute', 'minutes', n)))
    if now:
        t = now.timetuple()
    else:
        t = time.localtime()
    tz = None
    now = datetime.datetime(t[0], t[1], t[2], t[3], t[4], t[5], tzinfo=tz)
    delta = now - d
    since = delta.days * 24 * 60 * 60 + delta.seconds
    for i, (seconds, name) in enumerate(chunks):
        count = since / seconds
        if count != 0:
            break
    s = '%d %s' % (count, name(count))
    if i + 1 < len(chunks):
        # Now get the second item
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) / seconds2
        if count2 != 0:
            s += ', %d %s' % (count2, name2(count2))

    if s == "0 minutes":
        s = "about a minute... (checking)"
    return s


def timeuntil(d):
    now = datetime.datetime.now()
    return timesince(now, d)


class ScheduledTask(object):
    def __init__(self):
        self.mclient = memcache.Client(MEMCACHED_SERVERS, debug=0)
        self.cnx = None
        self.server_list = None
        self.sleep_time = 15

    def setup_log(self, ttype, maxBytes=None, backupCount=7):
        maxBytes = 1024 * 1024
        date_fmt = '%m/%d/%Y %H:%M:%S'
        log_formatter = logging.Formatter(
            u'[%(asctime)s] %(levelname)-7s: %(message)s )',
            datefmt=date_fmt)

        log_name = os.path.join("/tmp/%s.log" % ttype)

        handler = logging.handlers.RotatingFileHandler(
            log_name,
            maxBytes=maxBytes,
            backupCount=backupCount)

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
            tmp = {t: int(i)}
            dt = dtn + datetime.timedelta(**tmp)
        else:
            if ':' in ask:
                hour, minute = ask.split(':')
            elif 'h' in ask.lower():
                hour, minute = ask.lower().split('h')
            else:
                print "Invalid time format, needs to " + \
                    "be in the style of 15:10 or 15h10"
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
        self.server_list = self.cnx.servers.list()
        server_list_names = [s.name for s in self.server_list]
        lock = False
        for server in SERVER_NAMES:
            if server in server_list_names:
                lock = True
        return lock

    def logAndWait(self, image_id, ftype, ttype):
        previous_status = None

        while True:
            status = ftype.get(image_id).status
            if status != previous_status:
                previous_status = status
                if status == "UNKNOWN":
                    continue
                self.mclient.set("demo-cron-%sStatus" % (ttype), status)
                if self.options.verbose:
                    self.ssprint("%s " % (status))
            else:
                self.ssprint(".")
            if status == "ACTIVE":
                self.mclient.delete("demo-cron-%sStatus" % (ttype))
                return
            time.sleep(1)

    def do_backup(self, delete_server_after=True):
        self.get_cnx()
        if not self.server_list:
            self.server_list = self.cnx.servers.list()
        for server in self.server_list:
            if server.name in SERVER_NAMES:
                backup_image_name = "%s-%s" % (BACKUP_PREFIX, server.name)
                backuping = self.mclient.get("demo-cron-backupCurrentImage")
                if backuping:
                    print "backup going on exiting"
                    return
                self.mclient.set("demo-cron-backupCurrentImage", server.name)
                self.mclient.set("demo-cron-backupFlavorId%s" %
                                 (str(server.name)), server.flavorId)
                self.ssprint("[%s] " % (server.name))
                backup_image = self.cnx.images.create(backup_image_name,
                                                      server.id)
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
            '-o UserKnownHostsFile=/dev/null']
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
            if image.name.startswith("backup-") and \
                    sname in SERVER_NAMES:
                fId = self.mclient.get("demo-cron-backupFlavorId%s" % \
                                           (str(sname)))
                if fId:
                    fId = int(fId)
                    self.mclient.delete("demo-cron-backupFlavorId%s" %
                                        (str(sname)))
                else:
                    fId = IMAGE_DEFAULT_FLAVOR_ID

                self.ssprint("[%s] " % (sname))

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

        if not all([web_private_ip,
                    web_public_ip,
                    db_private_ip,
                    db_public_ip]):
            #TODO: Send mail!
            print "Error while recovering!"
            return

        self.mclient.set("demo-cron-restoreStatus", "ScriptWebNetworking")
        output = self.exec_cmd(web_public_ip,
                                ["./web-networking.sh", "demo-db1",
                                 db_private_ip])
        logging.getLogger(__name__).info(output)

        self.mclient.set("demo-cron-restoreStatus", "ScriptDBNetworking")
        output = self.exec_cmd(db_public_ip,
                               ["./db-networking.sh", "demo-web1",
                                web_private_ip])
        logging.getLogger(__name__).info(output)

        self.mclient.delete("demo-cron-restoreCurrentImage")

    def get_status(self, ttype):
        bCi = self.mclient.get("demo-cron-%sCurrentImage" % (ttype))
        if not bCi:
            print "Nothing going on"
            return
        return "%s:%s" % (
            self.mclient.get("demo-cron-%sCurrentImage" % (ttype)),
            self.mclient.get("demo-cron-%sStatus" % (ttype)))

    def testit(self):
        dtn = datetime.datetime.now()
        now = datetime.datetime(year=dtn.year,
                                month=dtn.month,
                                day=dtn.day,
                                hour=int(14),
                                minute=int(29))

        dtn = datetime.datetime.now()
        start = datetime.datetime(year=dtn.year,
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
        print SET_CRON_HELP
        dtn = datetime.datetime.now()

        start_time = self.ask_for_time('Start time: ')
        if dtn > start_time:
            print "Cannot set a time in the past."
            return
        self.mclient.set("demo-cron-start",
                         time.mktime(start_time.timetuple()))

        end_time = self.ask_for_time('End time: ')
        if start_time > end_time:
            print "End time cannot be before Start time"
            return
        self.mclient.set("demo-cron-end", time.mktime(end_time.timetuple()))
        #self.run_daemon()

    def main(self):
        opparser = optparse.OptionParser(
            usage="cron.py [options]")

        opparser.add_option('-b', '--backup',
                            dest="backup",
                            action="store_true",
                            help="Launch Backup")

        opparser.add_option('-r', '--restore',
                            dest="restore",
                            action="store_true",
                            help="Launch Restore")

        opparser.add_option('-c', '--set-cron',
                            dest="setcron",
                            action="store_true",
                            help="Set Cron.")

        opparser.add_option('--backup-status',
                            dest="backupStatus",
                            action="store_true",
                            help="Get backup status ")

        opparser.add_option('--restore-status',
                            dest="restoreStatus",
                            action="store_true",
                            help="Get restore status ")

        opparser.add_option('-k', '--cleanup',
                            dest="cleanup",
                            action="store_true",
                            help="Cleanup all locks session status.")

        opparser.add_option('-K', '--hard-cleanup',
                            dest="hard_cleanup",
                            action="store_true",
                            help="cleanup including servers and images.")

        opparser.add_option('-d', '--daemon',
                            dest="daemon",
                            action="store_true",
                            help="Launch cron daemons.")

        opparser.add_option('-v', '--verbose',
                            dest="verbose",
                            action="store_true",
                            help="Be verbose.")

        (options, args) = opparser.parse_args()  # pylint: disable-msg=W0612
        self.options = options

        if options.restore:
            self.do_restore()
        elif options.backup:
            self.do_backup()
        elif options.setcron:
            self.set_cron()
        elif options.backupStatus:
            print self.get_status("backup")
        elif options.restoreStatus:
            print self.get_status("restore")
        elif options.cleanup:
            self.cleanup()
        elif options.hard_cleanup:
            self.hard_cleanup()
            return
        #self.hard_cleanup()
        elif options.daemon:
            #TODO: Not a proper daemon yet!
            self.run_daemon()
        else:
            print "No arguments specified please see --help"
            return

    def cleanup(self):
        print "Cleaning up:"
        s = ["demo-cron-backupCurrentImage",
             "demo-cron-restoreCurrentImage",
             "demo-cron-restoreStatus",
             "demo-cron-restoreStatus",
             "demo-cron-end", "demo-cron-start"]
        for t in s:
            self.mclient.delete(t)

    def hard_cleanup(self):
        self.cleanup()
        self.get_cnx()
        for x in self.cnx.servers.list():
            if x.name in SERVER_NAMES:
                print "Deleting: %s" % (x.name)
                x.delete()

    def ssprint(self, s):
        if self.options.verbose:
            sys.stdout.write(s)
            sys.stdout.flush()

    def run_daemon(self):
        while True:
            mdstart = self.mclient.get("demo-cron-start")
            mdend = self.mclient.get("demo-cron-end")
            if not all([mdstart, mdend]):
                print "Cron not setup yet"
                return

            i_have_printed = False

            dtstart = datetime.datetime.fromtimestamp(mdstart)
            dtend = datetime.datetime.fromtimestamp(mdend)
            now = datetime.datetime.now()

            nh, nm = (now.hour, now.minute)
            sh, sm = (dtstart.hour, dtstart.minute)
            eh, em = (dtend.hour, dtend.minute)
            if nh == sh and nm == sm:
                iscreated = self.is_server_created()
                if not iscreated:
                    doingIt = self.mclient.get("demo-cron-backupCurrentImage")
                    if doingIt:
                        s, t = self.get_status("backup").split(":")
                        print "I am backuping %s status, is %s" % (s, t)
                        continue
                    else:
                        if not i_have_printed:
                            i_have_printed = True
                            print "I was going to backup but they" + \
                                " are already stored in images" + \
                                "so I am going to pass on this one."
                        time.sleep(self.sleep_time)
                        continue
                self.ssprint("Storing servers as images: ")
                self.do_backup()
                self.ssprint("Done.\n")
            elif nh == eh and nm == em:
                iscreated = self.is_server_created()
                if iscreated:
                    doingIt = self.mclient.get("demo-cron-recoverCurrentImage")
                    if doingIt:
                        s, t = self.get_status("recover").split(":")
                        print "I am recovering %s, status is %s" % (s, t)
                        continue
                    else:
                        print "TODO: This should not happen!"
                        continue
                self.ssprint("Restoring servers from backup: ")
                self.do_restore()

                ip = None
                for x in self.cnx.servers.list():
                    if x.name == "demo-web1":
                        ip = x._info['addresses']['public'][0]
                self.ssprint("\nServers has been restored, " + \
                "Go to http://demo-web1.dyndns.info or http://%s\n" \
                                 % (ip))
            else:
                if self.options.verbose:
                    iscreated = self.is_server_created()
                    if not iscreated and now >= dtstart:
                        print "Will start recovering in %s" % timeuntil(dtend)
                    else:
                        if now > dtstart:
                            print "Will start backup tomorrow at %s." % \
                                dtstart.strftime("%H:%M:%S")
                            self.sleep_time = 3600
                        else:
                            print "Will start backup in %s" % \
                                timeuntil(dtstart)
                            self.sleep_time = 15
                time.sleep(self.sleep_time)

if __name__ == '__main__':
    try:
        c = ScheduledTask()
        c.main()
    except(KeyboardInterrupt):
        pass
    #c.testit()
