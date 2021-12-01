#!/usr/bin/env python3
import random
import string
import password

import kauppa
import checkLogin
import createUser
import createProduct
import forum

import cherrypy

home_button = """<form method="get" action="index">
              <button type="submit">home</button>"""


class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        return """<html>
          <head></head>
          <body>
            <form method="get" action="login">
              <input type="text" value="testimies@mail.com" name="user_name" />
              <input type="text" value="pass" name="user_pass" />
              <button type="submit">login</button>
            </form>
            <form method="get" action="createUserMainMenu">
              <button type="submit">Create account</button>
            </form>
            <form method="get" action="shopMainMenu">
              <button type="submit">shop</button>
            </form>
            <form method="get" action="showLogin">
              <button type="submit">Show login</button>
            </form>
            <form method="get" action="boardMainMenu">
              <button type="submit">Forums</button>
            </form>
            <form method="get" action="showOrderHistory">
              <button type="submit">Order history</button>
            </form>
            <form method="get" action="logout">
              <button type="submit">logout</button>
            </form>
          </body>
        </html>"""

    @cherrypy.expose
    def showLogin(self):
        if cherrypy.session['session_id']:
            customer_id = cherrypy.session['customer_id']
            return ("Customer ID: "+str(customer_id) + home_button)
        else:
            return ("You're not logged in. "+ home_button)

    @cherrypy.expose
    def createUserMainMenu(self):
        return """<form method="get" action="createUser">
              <input type="text" value="First name" name="first_name" />
              <input type="text" value="Last name" name="last_name" />
              <br>
              <input type="text" value="e-mail" name="email" />
              <br>
              <input type="text" value="password" name="password" />
              <br>
              <button type="submit">create</button>
              <br>""" + home_button

    @cherrypy.expose
    def createProductMainMenu(self):
        return """<form method="get" action="createProduct">
              <input type="text" value="Product name" name="prod_name" />
              <br>
              <input type="text" value="Product price" name="prod_price" />
              <br>
              <input type="text" value="Product stock" name="stock" />
              <br>
              <button type="submit">create</button>
              <br>""" + home_button

    @cherrypy.expose
    def shopMainMenu(self):
        return """<form method="get" action="showProducts">
                  <button type="submit">Show products</button>
                  </form>
                  <br>
                  <form method="get" action="createProductMainMenu">
                  <button type="submit">Create product</button>
                  </form>
                  <br>""" + home_button

    @cherrypy.expose
    def showProducts(self):
        returnLst = []
        products = kauppa.getItems()
        for product in products:
            returnLst.append("<form method='get' action='productMenu'><button type='submit' name='prod_id' value="+str(product.uuid)+">"+product.prod_name+"</button></form><br>")
        return ''.join(returnLst) + home_button

    @cherrypy.expose
    def boardMainMenu(self):
        # TODO: this uses (soon to be) deprecated boardTree method
        returnLst = []
        root_boards = forum.boardTree(0)
        for board in root_boards:
            board_id = board[1]
            board_name = board[0]
            returnLst.append("<form method='get' action='goToBoard'><button name='board_id' value="+str(board_id)+" type='submit'>"+board_name+"</button></form></body></html>")
        return ''.join(returnLst)

    @cherrypy.expose
    def goToBoard(self, board_id):
        returnLst = []
        sub_boards = forum.showBoard(board_id)[0]
        chains = forum.showBoard(board_id)[1]
        for subs in sub_boards:
            returnLst.append("<form method='get' action='goToBoard'><button name='board_id' value="+subs[2]+" type='submit'>"+subs[0]+"</button></form></body></html>")
        for chain in chains:
            returnLst.append("<form method='get' action='goToChain'><button name='chain_id' value="+chain[2]+" type='submit'>"+chain[0]+"</button></form></body></html>")
        return ''.join(returnLst)

    @cherrypy.expose
    def goToChain(self, chain_id):
        returnLst = []
        comments = forum.showChain(chain_id)
        for comment in comments:
            returnLst.append(comment[2].strftime('%Y-%m-%d %H:%M:%S') + "<br>karma: " + str(comment[3]) + "<br>" + comment[0] + " commented: <br>" + comment[1] +"<br><br>")
    #        returnLst.append(comment[0] + ": " + comment[1] + " on " + comment[2].strftime('%Y-%m-%d %H:%M:%S'))
        return ''.join(returnLst)

    @cherrypy.expose
    def productMenu(self, prod_id):
        price = kauppa.getPrice(prod_id) / 100
        stock = kauppa.getStock(prod_id)
        name = kauppa.getProdName(prod_id)
        return "<html><head>"+str(name)+"</head><body><p>Price: "+str(price)+"€</p><p>Stock: "+str(stock)+" units.</p><br><form method='get' action='buyProduct'><button name='prod_id' value="+prod_id+" type='submit'>Buy "+str(name)+"!</button></form></body></html>"

    @cherrypy.expose
    def buyProduct(self, prod_id):
        session_id = cherrypy.session['session_id']
        customer_id = cherrypy.session['customer_id']
        order_id = kauppa.buy(prod_id, session_id, customer_id)
        return home_button

    @cherrypy.expose
    def createUser(self, first_name, last_name, email, password):
        createUser.createUser(first_name, last_name, email, password)

    @cherrypy.expose
    def createProduct(self, prod_name, prod_price, stock):
        createProduct.createProduct(prod_name, prod_price, stock)

    @cherrypy.expose
    def showOrderHistory(self):
        customer_id = cherrypy.session['customer_id']
        orders = kauppa.getOrderHistory(customer_id)
        return orders

    @cherrypy.expose
    # TODO: move checkCreds method here.
    def login(self, user_name, user_pass):
        userFound = checkLogin.checkCreds(user_name, user_pass)
        if userFound:
            loginCorrect = checkLogin.checkCreds(user_name, user_pass)[0]
            customer_id = checkLogin.checkCreds(user_name, user_pass)[1]
        else:
            return "Login incorrect"
        if loginCorrect:
            try:
                session = kauppa.login(str(customer_id))
                session_id = session[0]
            except Exception as err:
                return(str(err) + " kauppa.login failed.")
            cherrypy.session['session_id'] = session_id
            cherrypy.session['customer_id'] = customer_id
            cherrypy.session['user_name'] = user_name
            cherrypy.session['login_time'] = session[1]
            return ("login correct for "+str(customer_id)) + " " + user_name + home_button
        else:
            return "login incorrect"

    @cherrypy.expose
    def logout(self):
        try:
            session_id = cherrypy.session['session_id']
            customer_id = cherrypy.session['customer_id']
            login_time = cherrypy.session['login_time']
            kauppa.logout(session_id, customer_id, login_time)
            cherrypy.session['session_id'] = ""
            cherrypy.session['customer_id'] = ""
            cherrypy.session['user_name'] = ""
            return ("Logged out." + home_button)
        except Exception as err:
#            return ("You're not logged in." + home_button)
            return str(err)

if __name__ == '__main__':
#    cherrypy.quickstart(StringGenerator())
    conf = {
        '/': {
            'tools.sessions.on': True
        }
    }
    cherrypy.quickstart(StringGenerator(), '/', conf)