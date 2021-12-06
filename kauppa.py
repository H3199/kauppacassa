#!/usr/bin/env python3
#
# These functions make the queries into the DB
#
import createUser

import uuid
import password
import datetime
from cassandra.cluster import Cluster
from tabulate import tabulate
import db

session = db.session

def getInventory(item):
	query = ("SELECT inventory FROM inventory_counts WHERE uuid = " + item)
	rows = session.execute(query)
	for row in rows:
		print(row.inventory)
	Screen().input('Press [Enter] to continue')

def getStock(item):
	query = ("SELECT inventory FROM inventory_counts WHERE uuid = " + item)
	rows = session.execute(query)
	for row in rows:
		return row.inventory

def getPrice(item):
	query = ("SELECT prod_price FROM testable2 WHERE uuid = " + item)
	rows = session.execute(query)
	for row in rows:
		return row.prod_price

def showPrice(item):
	query = ("SELECT prod_price FROM testable2 WHERE uuid = " + item)
	rows = session.execute(query)
	for row in rows:
		print(row.prod_price / 100)	
	Screen().input('Press [Enter] to continue')

def getProdName(item):
	query = ("SELECT prod_name from testable2 WHERE uuid = " + item)
	rows = session.execute(query)
	for row in rows:
		return row.prod_name

def getItems():
	query = "SELECT uuid, prod_name FROM testable2"
	session.execute(query)
	rows = session.execute(query)
	return rows

def getCustomerList():
	query = "SELECT customer_id, last_name, first_name FROM customer_info"
	session.execute(query)
	rows = session.execute(query)
	return rows

def getOrderHistory(customer_id):
	query_order_history = ("SELECT order_id FROM order_history WHERE customer_id = "+str(customer_id))
	order_ids = session.execute(query_order_history)
	order_names = []
	order_prices = []
	order_costSum = []
	ordered = []
	status = []
	rated = []
	for order in order_ids:
		query_orderid_sessionid_customerid = ("SELECT product_id, ordered, status FROM orderid_sessionid_customerid WHERE order_id = "+str(order.order_id))
		rows = session.execute(query_orderid_sessionid_customerid)
		for row in rows:
			query_products = ("SELECT prod_name, prod_price FROM testable2 WHERE uuid = "+str(row.product_id))
			products = session.execute(query_products)
			for product in products:
				order_names.append(product.prod_name)
				order_costSum.append(product.prod_price)
				order_prices.append(str(product.prod_price / 100)+" €")
			#orders.append(str(row.product_id))
			ordered.append((str(row.ordered))[0:10])
			status.append(row.status)
			query_rating = ("SELECT rating from product_rating WHERE product_id = "+str(row.product_id)+" AND order_id = "+str(order.order_id))
			ratingRow = session.execute(query_rating)
			for rating in ratingRow:
				if rating.rating:
					rated.append(True)
				else:
					rated.append(False)
	total_cost = str(sum(order_costSum)/100)+" €"
	order_names.append("TOTAL")
	order_prices.append(total_cost)
	table = [order_names, order_prices, ordered, status]
	return (tabulate({'Products': order_names, 'Cost': order_prices, 'Ordered': ordered, 'Status': status, 'Rated': rated}, headers='keys', tablefmt='html', stralign='left'))


def buy(item, session_id, customer_id):
	price = getPrice(item)
	active_customer = str(customer_id)
	# TODO: check for balance first
	query_customer_balance = ("UPDATE customer_balance SET balance = balance - "+ str(price) +" WHERE customer_id = " + active_customer)
	session.execute(query_customer_balance)
	# TODO: check for stock first
	query_stock = ("UPDATE inventory_counts SET inventory = inventory - 1 WHERE uuid = " + item)
	session.execute(query_stock)
	order_id = str(uuid.uuid4())
	now_iso8601 = datetime.datetime.now()
	now = str(int(now_iso8601.timestamp()*1000))
	query_order_history = ("INSERT INTO order_history (customer_id, order_id) VALUES ("+active_customer+", "+order_id+")")
	query_orderid_sessionid_customerid = ("INSERT INTO orderid_sessionid_customerid (order_id, session_id, customer_id, ordered, product_id, status) VALUES ("+order_id+", "+str(session_id)+", "+active_customer+", \'"+now+"\', "+item+", \'ordered\')")
	# Create entry for product rating:
	query_product_rating = ("INSERT INTO product_rating (product_id, order_id) VALUES ("+item+", "+order_id+")")
	session.execute(query_orderid_sessionid_customerid)
	session.execute(query_order_history)
	session.execute(query_product_rating)
	return order_id

def rate(product_id, order_id, rating): # This could be done with just order_id and rating, but that would use an additional DB query.
	if not 0 <= rating <= 5:
		return False
	# Check if this order has already been rated:
	check_product_rating = ("SELECT rating FROM product_rating WHERE product_id = "+product_id+" AND order_id = "+order_id)
	rated = session.execute(check_product_rating)
	for rate in rated:
		if rate.rating:
			return False
	update_product_rating = ("UPDATE product_rating SET rating = "+str(rating)+" WHERE product_id = "+product_id+" AND order_id = "+order_id)
	session.execute(update_product_rating)
	return True

def getRating(product_id):
	ratelst = []
	get_product_ratings = ("SELECT rating FROM product_rating WHERE product_id = "+product_id)
	ratings = session.execute(get_product_ratings)
	for rate in ratings:
		if rate.rating:
			ratelst.append(rate.rating)
	if len(ratelst) != 0:
		return sum(ratelst) / len(ratelst)
	else:
		return "product has not been rated yet."

def login(customer_id):
	customer = str(customer_id)
	session_id = str(uuid.uuid4())
	now_iso8601 = datetime.datetime.now()
	now = str(int(now_iso8601.timestamp()*1000))
	query_login_sessions = ("INSERT INTO login_sessions (session_id, customer_id, login) VALUES ("+session_id+", "+customer+", \'"+now+"\')")
	query_login_times = ("INSERT INTO login_times (session_id, customer_id, login) VALUES ("+session_id+","+customer+", \'"+now+"\')")
	query_customer_sessions = ("INSERT INTO customer_sessions (session_id, customer_id, login) VALUES ("+session_id+", "+customer+", \'"+now+"\')")
	session.execute(query_login_sessions)
	session.execute(query_login_times)
	session.execute(query_customer_sessions)
	return [session_id, now]

def getLogin(session_id):
	query = ("SELECT customer_id FROM customer_sessions WHERE session_id = " + session_id)
	rows = session.execute(query)
	for row in rows:
		return row.customer_id

#def logout(customer_id):
def logout(session_id, customer_id, login_time):
#	session_id = getLogin(customer_id)
	now_iso8601 = datetime.datetime.now()
	now = str(int(now_iso8601.timestamp()*1000))
	session_id = str(session_id)
	customer_id = str(customer_id)
	query_customer_sessions = ("UPDATE customer_sessions SET logout = \'"+now+"\' WHERE session_id = "+session_id)
	query_login_sessions = ("UPDATE login_sessions SET logout = \'"+now+"\' WHERE session_id = "+session_id+" AND customer_id = "+customer_id+" IF EXISTS")
	query_login_times = ("UPDATE login_times SET logout = \'"+now+"\' WHERE customer_id = "+customer_id+" AND login = \'"+login_time+"\' IF EXISTS")
	session.execute(query_customer_sessions)
	session.execute(query_login_sessions)
	session.execute(query_login_times)