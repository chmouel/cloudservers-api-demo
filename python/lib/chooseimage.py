#!/usr/bin/python
# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
from chooseserver import ChooseServer
from images import Images

class ChooseImage(ChooseServer):
    def __init__(self, CNX=None):
        self.cnx=CNX
        if not self.cnx:
            from common import CNX
            self.cnx = CNX

        _imageobj = Images(self.cnx)
        self.servers = _imageobj.local_images
        
if __name__ == '__main__':
    c = ChooseImage()
    print c.get_list_of_servers()
