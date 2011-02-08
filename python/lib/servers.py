#!/usr/bin/python
# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
from images import Images

class Servers(Images):
    def __init__(self, CNX):
        self.all_servers = CNX.servers.list()
        self.all_servers.sort(key=lambda x: x.name.lower())
        self.all_images = self.all_servers
        self.current = 0
        self.high = len(self.all_servers)

if __name__ == '__main__':
    from lib.common import CNX
    s = Servers(CNX)
    print s()
