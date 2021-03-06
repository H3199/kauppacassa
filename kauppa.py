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


def getInventory(item: str):
    query = ("SELECT inventory FROM inventory_counts WHERE uuid = " + item)
    rows = session.execute(query)
    for row in rows:
        print(row.inventory)
    Screen().input('Press [Enter] to continue')


def getStock(item: str):
    query = ("SELECT inventory FROM inventory_counts WHERE uuid = " + item)
    rows = session.execute(query)
    for row in rows:
        return row.inventory


def getPrice(item: str):
    query = ("SELECT prod_price FROM testable2 WHERE uuid = " + str(item))
    rows = session.execute(query)
    for row in rows:
        return row.prod_price


def showPrice(item: str):
    query = ("SELECT prod_price FROM testable2 WHERE uuid = " + item)
    rows = session.execute(query)
    for row in rows:
        print(row.prod_price / 100)
    Screen().input('Press [Enter] to continue')


def getProdName(item: str):
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
    query_order_history = ("SELECT order_id FROM order_history WHERE customer_id = " + str(customer_id))
    order_ids = session.execute(query_order_history)
    order_names = []
    order_prices = []
    order_costSum = []
    ordered = []
    status = []
    rated = []
    for order in order_ids:
        query_orderid_sessionid_customerid = (
                    "SELECT product_id, ordered, status FROM orderid_sessionid_customerid WHERE order_id = " + str(
                order.order_id))
        rows = session.execute(query_orderid_sessionid_customerid)
        for row in rows:
            query_products = ("SELECT prod_name, prod_price FROM testable2 WHERE uuid = " + str(row.product_id))
            products = session.execute(query_products)
            for product in products:
                order_names.append(product.prod_name)
                order_costSum.append(product.prod_price)
                order_prices.append(str(product.prod_price / 100) + " ???")
            # orders.append(str(row.product_id))
            ordered.append((str(row.ordered))[0:10])
            status.append(row.status)
            query_rating = ("SELECT rating from product_rating WHERE product_id = " + str(
                row.product_id) + " AND order_id = " + str(order.order_id))
            ratingRow = session.execute(query_rating)
            for rating in ratingRow:
                if rating.rating:
                    rated.append(True)
                else:
                    rated.append(False)
    total_cost = str(sum(order_costSum) / 100) + " ???"
    order_names.append("TOTAL")
    order_prices.append(total_cost)
    table = [order_names, order_prices, ordered, status]
    return (
        tabulate({'Products': order_names, 'Cost': order_prices, 'Ordered': ordered, 'Status': status, 'Rated': rated},
                 headers='keys', tablefmt='html', stralign='left'))


def buy(item: str, session_id: str, customer_id: str):
    price = getPrice(item)
    active_customer = str(customer_id)
    # TODO: check for balance first
    query_customer_balance = ("UPDATE customer_balance SET balance = balance - " + str(
        price) + " WHERE customer_id = " + active_customer)
    session.execute(query_customer_balance)
    # TODO: check for stock first
    query_stock = ("UPDATE inventory_counts SET inventory = inventory - 1 WHERE uuid = " + item)
    session.execute(query_stock)
    order_id = str(uuid.uuid4())
    now_iso8601 = datetime.datetime.now()
    now = str(int(now_iso8601.timestamp() * 1000))
    query_order_history = (
                "INSERT INTO order_history (customer_id, order_id) VALUES (" + active_customer + ", " + order_id + ")")
    query_orderid_sessionid_customerid = (
                "INSERT INTO orderid_sessionid_customerid (order_id, session_id, customer_id, ordered, product_id, status) VALUES (" + order_id + ", " + str(
            session_id) + ", " + active_customer + ", \'" + now + "\', " + item + ", \'ordered\')")
    # Create entry for product rating:
    query_product_rating = ("INSERT INTO product_rating (product_id, order_id) VALUES (" + item + ", " + order_id + ")")
    session.execute(query_orderid_sessionid_customerid)
    session.execute(query_order_history)
    session.execute(query_product_rating)
    return order_id


def orderCart(cart_id, session_id, customer_id):
    get_product_list = ("SELECT product_id, count FROM cart_contents WHERE cart_id = " + cart_id)
    product_list = session.execute(get_product_list)
    for product in product_list:
        for i in range(int(product.count)):
            buy(str(product.product_id), str(session_id), str(customer_id))
    clearCart(cart_id)


def clearCart(cart_id):
    delete_cart = ("DELETE FROM cart_contents WHERE cart_id = "+str(cart_id))
    session.execute(delete_cart)
    # return True


def saveCart(session_id):
    set_save = ("UPDATE session_carts SET saved = True WHERE session_id = "+str(session_id))
    session.execute(set_save)
    return True


def addToCart(cart_id, product_id):
    get_product_count = (
                "SELECT count FROM cart_contents WHERE cart_id = " + cart_id + " AND product_id = " + product_id)
    product_count = session.execute(get_product_count)
    count = None
    for product in product_count:
        count = product.count
    if count:
        count += 1
        update_cart_contents = ("UPDATE cart_contents SET count = " + str(
            count) + " WHERE cart_id = " + cart_id + " AND product_id = " + product_id)
    else:
        update_cart_contents = (
                    "INSERT INTO cart_contents (cart_id, product_id, count) VALUES (" + cart_id + ", " + product_id + ", 1)")
    session.execute(update_cart_contents)


def removeFromCart(cart_id, product_id):
    get_product_count = ("SELECT count FROM cart_contents WHERE cart_id = " + cart_id + " AND product_id = " + product_id)
    product_count = session.execute(get_product_count)
    count = None
    for product in product_count:
        count = product.count
    if count > 1:
        count -= 1
        update_cart_contents = ("UPDATE cart_contents SET count = " + str(count) + " WHERE cart_id = " + cart_id + " AND product_id = " + product_id)
        session.execute(update_cart_contents)
    elif count == 1:
        update_cart_contents = ("DELETE FROM cart_contents WHERE cart_id = "+str(cart_id)+" AND product_id = "+str(product_id))
        session.execute(update_cart_contents)


def displayCart(cart_id):
    product_names = []
    product_prices = []
    product_counts = []
    product_totals = []
    get_cart_contents = ("SELECT product_id, count FROM cart_contents WHERE cart_id = " + str(cart_id))
    products = session.execute(get_cart_contents)
    for product in products:
        #add_products.append([str(cart_id), str(product.product_id)])
        #rem_products.append([str(cart_id), str(product.product_id)])
        if product.count:
            product_counts.append(product.count)
        else:
            product_counts.append(0)
        get_product_info = ("SELECT prod_name, prod_price FROM testable2 WHERE uuid = " + str(product.product_id))
        product_info = session.execute(get_product_info)
        for info in product_info:
            product_names.append(info.prod_name)
            product_prices.append((str(info.prod_price / 100) + " ???"))
            product_totals.append(info.prod_price * product.count)
    total_cost = str(sum(product_totals) / 100) + " ???"
    product_names.append("Total: ")
    product_prices.append(total_cost)
    return (tabulate({'Products': product_names, 'Cost': product_prices, 'Count': product_counts}, headers='keys',
                     tablefmt='html', stralign='left'))


def rate(product_id, order_id, rating):
    if not 0 <= rating <= 5:
        return False
    # Check if this order has already been rated:
    check_product_rating = (
                "SELECT rating FROM product_rating WHERE product_id = " + product_id + " AND order_id = " + order_id)
    rated = session.execute(check_product_rating)
    for rate in rated:
        if rate.rating:
            return False
    update_product_rating = ("UPDATE product_rating SET rating = " + str(
        rating) + " WHERE product_id = " + product_id + " AND order_id = " + order_id)
    session.execute(update_product_rating)
    return True


def getRating(product_id):
    ratelst = []
    get_product_ratings = ("SELECT rating FROM product_rating WHERE product_id = " + product_id)
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
    cart_id = str(uuid.uuid4())
    now_iso8601 = datetime.datetime.now()
    now = str(int(now_iso8601.timestamp() * 1000))
    query_login_sessions = (
                "INSERT INTO login_sessions (session_id, customer_id, login) VALUES (" + session_id + ", " + customer + ", \'" + now + "\')")
    query_login_times = (
                "INSERT INTO login_times (session_id, customer_id, login) VALUES (" + session_id + "," + customer + ", \'" + now + "\')")
    query_customer_sessions = (
                "INSERT INTO customer_sessions (session_id, customer_id, login) VALUES (" + session_id + ", " + customer + ", \'" + now + "\')")
    create_cart = ("INSERT INTO session_carts (session_id, cart_id) VALUES (" + session_id + ", " + cart_id + ")")
    session.execute(query_login_sessions)
    session.execute(query_login_times)
    session.execute(query_customer_sessions)
    session.execute(create_cart)
    return [session_id, now, cart_id]


def getLogin(session_id):
    query = ("SELECT customer_id FROM customer_sessions WHERE session_id = " + session_id)
    rows = session.execute(query)
    for row in rows:
        return row.customer_id

# Why does logging out need login_time?
def logout(session_id, customer_id, login_time, cart_id=None):
    #	session_id = getLogin(customer_id)
    now_iso8601 = datetime.datetime.now()
    now = str(int(now_iso8601.timestamp() * 1000))
    session_id = str(session_id)
    customer_id = str(customer_id)
    query_cart_saved = ("SELECT saved FROM session_carts WHERE session_id = "+session_id)
    cart_saved_r = session.execute(query_cart_saved)
    for r in cart_saved_r:
        cart_saved = r.saved
    query_customer_sessions = ("UPDATE customer_sessions SET logout = \'" + now + "\' WHERE session_id = " + session_id)
    query_login_sessions = (
                "UPDATE login_sessions SET logout = \'" + now + "\' WHERE session_id = " + session_id + " AND customer_id = " + customer_id + " IF EXISTS")
    query_login_times = (
                "UPDATE login_times SET logout = \'" + now + "\' WHERE customer_id = " + customer_id + " AND login = \'" + login_time + "\' IF EXISTS")
    if cart_id and not cart_saved:
        clearCart(cart_id)
    session.execute(query_customer_sessions)
    session.execute(query_login_sessions)
    session.execute(query_login_times)
