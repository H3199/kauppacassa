#!/usr/bin/env python3

import uuid
import password
import datetime
from cassandra.cluster import Cluster
import db

session = db.session

def comment(user_id, chain_id, comment):
	now_iso8601 = datetime.datetime.now()
	now = str(int(now_iso8601.timestamp()*1000))
	comment_id = str(uuid.uuid4())
	query_comments = ("INSERT INTO comments (comment_id, chain_id, user_id, timestamp, comment) VALUES ("+comment_id+", "+chain_id+", "+user_id+", \'"+now+"\', \'"+comment+"\')")
	query_chains = ("INSERT INTO com_chain12 (chain_id, comment_id, timestamp) VALUES ("+chain_id+", "+comment_id+", \'"+now+"\')")
#	print(query_comments)
#	print(query_chains)
	session.execute(query_comments)
	session.execute(query_chains)

def showChain(chain_id):
	query_chains = ("SELECT comment_id FROM com_chain12 WHERE chain_id = "+str(chain_id))
	comments = []
	rows=session.execute(query_chains)
	for row in rows:
		comment_id = row.comment_id
		query_comments = ("SELECT user_id, comment, timestamp FROM comments WHERE comment_id= "+str(comment_id))
		get_comments=session.execute(query_comments)
	#print (get_comments)
		for comment in get_comments:
			# Get name of the user_id
			query_customer_info = ("SELECT first_name, last_name FROM customer_info WHERE customer_id = "+str(comment.user_id))
			name_rows = session.execute(query_customer_info)
			for name_row in name_rows:
				name = (name_row.first_name + " " + name_row.last_name)
			comments.append([name, comment.comment, comment.timestamp])
	for i in comments:
		print(i[0] + ": " + i[1] + " on " + i[2].strftime('%Y-%m-%d %H:%M:%S'))