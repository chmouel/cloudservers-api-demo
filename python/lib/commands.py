# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
import os
import tempfile
from subprocess import call


def copy_exec_script(public_ip, script, args=[], username='root'):
    common_options = ['-q',
                   '-o StrictHostKeyChecking=no',
                   '-o UserKnownHostsFile=/dev/null']

    tmpname = os.path.join("/tmp",
                           os.path.basename(tempfile.mktemp("-cloudscripts")))
    call('scp %s %s %s@%s:%s' % \
             (" ".join(common_options), script, username,
              public_ip, tmpname), shell=True)

    call('ssh -t -x %s %s@%s "%s %s && rm -f %s"' %  \
             (" ".join(common_options), username,
              public_ip, tmpname, " ".join(args), tmpname), shell=True)

if __name__ == '__main__':
    copy_exec_script(os.environ.get('IP'), '/tmp/a.sh',
                     args=["Hello2", "Bar"])
