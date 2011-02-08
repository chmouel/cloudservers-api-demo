#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Chmouel Boudjnah <chmouel@chmouel.com>
from lib.images import Images
from lib.common import CNX

if __name__ == '__main__':
    servers = []
    i = Images(CNX)
    for n in i.local_images:
        print "%d - %s" % (n.id, n.name)

