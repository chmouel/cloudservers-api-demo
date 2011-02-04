#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Chmouel Boudjnah <chmouel@chmouel.com>
from lib.common import CNX

if __name__ == '__main__':
    x = CNX.servers.list();
    for n in sorted(x):
        print "%s - %s " % (n.name, n.public_ip)

