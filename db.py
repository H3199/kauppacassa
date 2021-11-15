#!/usr/bin/env python3

from cassandra.cluster import Cluster

cluster = Cluster(['172.18.0.2'],port=9042)
session = cluster.connect('testi',wait_for_all_pools=True)
session.execute('USE testi')