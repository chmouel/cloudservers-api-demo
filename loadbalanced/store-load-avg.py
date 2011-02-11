#!/usr/bin/python
# -*- encoding: utf-8 -*-
import os
import memcache

MEMCACHED_SERVERS=["loadbalancer.local:11211"]

def myhostname():
    return os.uname()[1].split(".")[0]

def detect_loadavg(load_avg_file='/proc/loadavg'):
    data = open(load_avg_file, 'r').readline().strip().split()
    return map(float, data[:3])

def main():
    l1, l2, l3 = detect_loadavg()

    mclient = memcache.Client(MEMCACHED_SERVERS, debug=0)
    label1m = "%s-l1" % (myhostname())
    mclient.set(label1m, l1)

if __name__ == '__main__':
    main()
