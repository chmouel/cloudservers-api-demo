#!/usr/bin/python
# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
from chooseserver import ChooseServer

class ChooseImage(ChooseServer):
    def __init__(self, CNX=None):
        self.cnx=CNX
        if not self.cnx:
            from common import CNX
            self.cnx = CNX

        self.servers = []
        for x in self.cnx.images.list():
            if not 'created' in x._info:
                continue
            self.servers.append(x)
        
if __name__ == '__main__':
    c = ChooseImage()
    print c.get_list_of_servers()
