#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Chmouel Boudjnah <chmouel@chmouel.com>
from lib.common import CNX

if __name__ == '__main__':
    servers = []
    for x in CNX.images.list():
        if not 'created' in x._info:
            continue
        servers.append(x)

    for n in sorted(servers):
        print "%d - %s" % (n.id, n.name)

