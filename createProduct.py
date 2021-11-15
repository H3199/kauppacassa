#!/usr/bin/env python3

import uuid
from cassandra.cluster import Cluster
from consolemenu import *
from consolemenu.items import *

cluster = Cluster(['172.21.0.2'],port=9042)
session = cluster.connect('testi',wait_for_all_pools=True)
session.execute('USE testi')

def createProduct(prod_name, prod_price, stock):
	prod_id = str(uuid.uuid4())
#	query_info = ("INSERT INTO customer_info (customer_id, email, first_name, last_name) VALUES ("+ID+", \'"+email+"\', \'"+first_name+"\', \'"+last_name+"\')")
	query_product_info = ("INSERT INTO testable2 (uuid, prod_name, prod_price, timestamp) VALUES ("+prod_id+", \'"+prod_name+"\', "+prod_price+", dateof(now()))")
	query_product_stock = ("UPDATE inventory_counts SET inventory = inventory + "+stock+ " WHERE uuid = "+prod_id+"")
#	print(query_product_stock)
#	print(query_product_info)
	session.execute(query_product_info)
	session.execute(query_product_stock)

def promptUser():
	print('Enter product name')
	prod_name = input()
	print('Enter product price:')
	prod_price = input()
	print('Enter the amount of stock for product:')
	stock = input()
	return [prod_name, prod_price, stock]

def main():
	prod_details = promptUser()
	createProduct(str(prod_details[0]), str(prod_details[1]), str(prod_details[2]),)

if __name__ == "__main__":
	main()
