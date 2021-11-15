#!/usr/bin/env python3

import uuid
import password
from cassandra.cluster import Cluster
import db

session = db.session

# TODO: trying to log in with non-existing user gives err 500

class User():
	password = password.Password(method='sha1', hash_encoding='base64')

def checkCreds(email, password_input):
	# TODO fix for non-existing email
	# Extract things from the DB
	get_uuid_query = "SELECT customer_id FROM uuid_by_email WHERE email = \'"+email+"\'"
	rows = session.execute(get_uuid_query)
	for row in rows:
		customer_id = row.customer_id
	get_saltedhash_query = ("SELECT password, salt FROM customer_pw WHERE customer_id = "+str(customer_id))
	rows = session.execute(get_saltedhash_query)
	for row in rows:
		hashed = row.password
		salt = row.salt

	# Test the pw in db vs pw input
	user = User()
	user.hash = hashed
	user.salt = salt
	return [user.password == password_input, customer_id]

def promptUser():
	print('Enter your email:')
	email = input()
	print('Enter your password')
	password_input = input()
	return [email, password_input]

if __name__ == "__main__":
	creds = promptUser()
	check = checkCreds(str(creds[0]), str(creds[1]))
	if check:
		print("password correct")
	else:
		print("password incorrect")