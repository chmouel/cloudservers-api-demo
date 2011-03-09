#!/usr/bin/python
# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
from servers import Servers

class ChooseServer(object):
    def __init__(self, CNX=None):
        self.cnx=CNX
        if not self.cnx:
            from common import CNX
            self.cnx = CNX
        _s = Servers(self.cnx)
        self.servers = _s()
        
    def match_server_to_sorted_number(self, ans):
        ret=None
        ans=int(ans)
        i=0
        for server in sorted(self.servers):
            if i == ans:
                ret=server
                break
            i+=1
        return ret

    def get_list_of_servers(self, ans=None):
        if not ans:
            i=0
            for server in sorted(self.servers):
                print "%d) %s" % (i, server.name)
                i+=1

            print "Enter a number or multiples (ie: 1 2 3) or a word match (ie: web would match all servers who has web in the imagename case insensitive)"
            ans = raw_input("=> ")

        if not ans:
            return
        
        server_numbers=[]
        if ans.isdigit():
            server_numbers=[self.match_server_to_sorted_number(ans)]
        else:
            for field in ans.split(" "):
                if field.isdigit():
                    server_numbers.append(self.match_server_to_sorted_number(field))
                else:
                    server_numbers.extend (
                        [ x for x in self.servers if field.lower() in x.name.lower()  ]
                        )
                
        return set(server_numbers)
            
if __name__ == '__main__':
    import os
    os.environ["RCLOUD_DATACENTER"] = "uk"

    b = ChooseServer();
    print b.get_list_of_servers()
