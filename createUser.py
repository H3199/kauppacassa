#!/usr/bin/env python3

import uuid
import password
from cassandra.cluster import Cluster
import db

session = db.session

class User():
	password = password.Password(method='sha1', hash_encoding='base64')

def createUser(first_name, last_name, email, password):
	ID = str(uuid.uuid4())
	user = User()
	user.password = password
	query_info = ("INSERT INTO customer_info (customer_id, email, first_name, last_name) VALUES ("+ID+", \'"+email+"\', \'"+first_name+"\', \'"+last_name+"\')")
	query_pw = ("INSERT INTO customer_pw (customer_id, password, salt) VALUES ("+ID+", \'"+user.hash+"\', \'"+user.salt+"\')")
	query_balance = ("UPDATE customer_balance SET balance = balance + 0 WHERE customer_id = "+ID+"")
	query_mail_table = ("INSERT INTO uuid_by_email (email, customer_id) VALUES (\'"+email+"\', "+ID+")")
#	print(query_info)
#	print(query_pw)
	session.execute(query_info)
	session.execute(query_pw)
	session.execute(query_balance)
	session.execute(query_mail_table)

def promptUser():
	print('Enter your first name:')
	first_name = input()
	print('Enter your last name:')
	last_name = input()
	print('Enter your email:')
	email = input()
	print('Enter your password')
	password = input()
	return [first_name, last_name, email, password]

if __name__ == "__main__":
	user_details = promptUser()
	createUser(str(user_details[0]), str(user_details[1]), str(user_details[2]), str(user_details[3]))