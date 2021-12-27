#!/usr/bin/env python3

from cassandra.cluster import Cluster

# DB connection is currently done via ssh and port forwarding
cluster = Cluster(['127.0.0.1'],port=9043)
session = cluster.connect('testi',wait_for_all_pools=True)
session.execute('USE testi')
