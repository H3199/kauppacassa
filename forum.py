#!/usr/bin/env python3

import uuid
import password
import datetime
import db

session = db.session

def comment(user_id, chain_id, comment):
	now_iso8601 = datetime.datetime.now()
	now = str(int(now_iso8601.timestamp()*1000))
	comment_id = str(uuid.uuid4())
	query_comments = ("INSERT INTO comments (comment_id, chain_id, user_id, timestamp, comment) VALUES ("+comment_id+", "+chain_id+", "+user_id+", \'"+now+"\', \'"+comment+"\')")
	query_chains = ("INSERT INTO com_chain12 (chain_id, comment_id, timestamp) VALUES ("+chain_id+", "+comment_id+", \'"+now+"\')")
	query_karma = ("UPDATE comment_karma SET karma = karma + 0 WHERE comment_id = "+comment_id)
	session.execute(query_comments)
	session.execute(query_chains)
	session.execute(query_karma)

def vote(comment_id, direction):
	upvote = ("UPDATE comment_karma SET karma = karma + 1 WHERE comment_id = "+str(comment_id))
	downvote = ("UPDATE comment_karma SET karma = karma - 1 WHERE comment_id = "+str(comment_id))
	if direction == "up":
		session.execute(upvote)
	if direction == "down":
		session.execute(downvote)

def showChain(chain_id):
	query_chains = ("SELECT comment_id FROM com_chain12 WHERE chain_id = "+str(chain_id))
	comments = []
	rows = session.execute(query_chains)
	for row in rows:
		if row.comment_id:
			comment_id = row.comment_id
			query_comments = ("SELECT user_id, comment, timestamp FROM comments WHERE comment_id= "+str(comment_id))
			get_comments = session.execute(query_comments)
			for comment in get_comments:
				# Get name of the user_id
				query_customer_info = ("SELECT first_name, last_name FROM customer_info WHERE customer_id = "+str(comment.user_id))
				query_karma = ("SELECT karma FROM comment_karma WHERE comment_id = " + str(comment_id))
				karma_rows = session.execute(query_karma)
				for karma_row in karma_rows:
					if karma_row.karma:
						karma = karma_row.karma
					else:
						karma = 0
				name_rows = session.execute(query_customer_info)
				for name_row in name_rows:
					name = (name_row.first_name + " " + name_row.last_name)
				comments.append([name, comment.comment, comment.timestamp, karma])
	return comments

def showBoard(board_id):
	chain_list = []
	sub_board_list = []
	# Get the chains in the board
	query_for_chains = ("SELECT chain_id FROM com_boards WHERE board_id = "+board_id)
	chains = session.execute(query_for_chains)
	for chain in chains:
		if chain.chain_id:
			query_chains = ("SELECT chain_name, timestamp FROM com_chain12 WHERE chain_id = "+str(chain.chain_id))
			rows = session.execute(query_chains)
			for row in rows:
				if row.chain_name: # Entries with no name are comments.
					chain_list.append([row.chain_name, row.timestamp, str(chain.chain_id)])
	# Get the sub boards of the board
	query_for_sub_boards = ("SELECT child_id FROM board_children WHERE board_id = "+board_id)
	sub_boards = session.execute(query_for_sub_boards)
	for board in sub_boards:
		if board.child_id:
			query_boards = ("SELECT board_name, timestamp FROM com_boards WHERE board_id = "+str(board.child_id))
			rows = session.execute(query_boards)
			for row in rows:
				if row.board_name:
					sub_board_list.append([row.board_name, row.timestamp, str(board.child_id)])
	return [sub_board_list, chain_list]

def boardTree(level):
	query_boards = ("SELECT board_id, board_name, parent_board_id FROM com_boards")
	boards = session.execute(query_boards)
	root_boards = []
	sub_boards = [] # "We" will add dynamic levels "later". Perhaps add board level in the DB?
	# - ok board level added in DB level, now what? How does a board know it's level?
	# - child/parent relation tables added in DB, use them to make this make sense.
	# - this function is pretty much obsolete now thanks to child/parent logic
	for board in boards:
		if board.board_name:
			if not board.parent_board_id:
				root_boards.append([board.board_name, board.board_id])
			if board.parent_board_id:
				sub_boards.append([board.board_name, board.board_id])
	if level == 0:
		return(root_boards)
	if level == 1:
		return(sub_boards)

def createChain(chain_name, board_id):
	now_iso8601 = datetime.datetime.now()
	now = str(int(now_iso8601.timestamp()*1000))
	chain_id = str(uuid.uuid4())
	query_chains = ("INSERT INTO com_chain12 (chain_id, timestamp, chain_name, board_id) VALUES ("+chain_id+", \'"+now+"\', \'"+chain_name+"\', "+board_id+")")
	query_boards = ("INSERT INTO com_boards (board_id, timestamp, chain_id) VALUES ("+board_id+", \'"+now+"\', "+chain_id+")")
	session.execute(query_chains)
	session.execute(query_boards)

def createBoard(board_name, parent_id=None, board_level=-1):
	now_iso8601 = datetime.datetime.now()
	now = str(int(now_iso8601.timestamp()*1000))
	board_id = str(uuid.uuid4())
	# Case where the created board has a parent:
	if parent_id:
		query_boards = ("INSERT INTO com_boards (board_id, timestamp, board_name, parent_board_id) VALUES ("+board_id+", \'"+now+"\', \'"+board_name+"\', "+parent_id+")")
		# Parent knows its children:
		update_parent = ("INSERT INTO board_children (board_id, child_id, board_level) VALUES ("+parent_id+", "+board_id+", "+str(board_level)+")")
		# Child knows its parent:
		update_child = ("INSERT INTO board_parent (board_id, parent_id, board_level) VALUES ("+board_id+", "+parent_id+", "+str(board_level)+")")
		session.execute(update_parent)
		session.execute(update_child)
	else:
		# This should only happen for a root board:
		query_boards = ("INSERT INTO com_boards (board_id, timestamp, board_name) VALUES ("+board_id+", \'"+now+"\', \'"+board_name+"\')")
	session.execute(query_boards)