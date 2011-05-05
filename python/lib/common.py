#!/usr/bin/python
# -*- encoding: utf-8 -*-
__author__ = "Chmouel Boudjnah <chmouel@chmouel.com>"
import os
import cloudservers

UK = True
if 'RCLOUD_DATACENTER' in os.environ:
    if os.environ['RCLOUD_DATACENTER'].lower() == "us":
        UK = False
else:
    answer = raw_input("US or UK (default: UK): ")
    if answer.lower() == "us":
        UK = False

US_CLOUDUSER = os.environ.get('US_RCLOUD_USER', '')
US_CLOUDKEY = os.environ.get('US_RCLOUD_KEY', '')
US_AUTHSERVER = os.environ.get('US_RCLOUD_AURL', '')

UK_CLOUDUSER = os.environ.get('UK_RCLOUD_USER', '')
UK_CLOUDKEY = os.environ.get('UK_RCLOUD_KEY', '')
UK_AUTHSERVER = os.environ.get('UK_RCLOUD_AURL', '')

#End Configuration

if UK:
    CLOUDUSER = UK_CLOUDUSER
    CLOUDKEY = UK_CLOUDKEY
    AUTHSERVER = UK_AUTHSERVER
else:
    CLOUDUSER = US_CLOUDUSER
    CLOUDKEY = US_CLOUDKEY
    AUTHSERVER = US_AUTHSERVER

CNX = cloudservers.CloudServers(CLOUDUSER,
                                CLOUDKEY,
                                auth_url=AUTHSERVER)

def i_am_about(msg, server_list):
    print "%s: "  % msg
    for server in server_list:
        print server.name, " ",
    print
    ans = raw_input("Pres Y to confirm or any other keys to cancel: ")
    if ans.lower() == "y":
        return True
    return False
