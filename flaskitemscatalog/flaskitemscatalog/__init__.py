
from flask import Flask

# basic configurations
app = Flask(__name__)

# some basic imports
import bleach
import requests
import string
import random
import string
import random
import httplib2
import json

# flask imports
from flask import Flask, render_template
from flask import request, url_for, redirect
from flask import jsonify, flash, make_response
from flask import session as login_session

# imports for OAuth 2 for google sign in
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# sports items database import
from flaskitemscatalog.sportsitems_db import CRUD
from flaskitemscatalog.sportsitems_db import main as DB_Main
#from flaskitemscatalog.fill_db import fillDB

# initialize DB
from os.path import isfile, getsize
#DB_Main()
#if not isfile("sportsitems.db"):
#    fillDB()
crud = CRUD()

# read client secret
CLIENT_ID = json.loads(
    open('/var/www/flaskitemscatalog/flasitemscatalog/client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "SportsItems"

# home page route
@app.route("/")
@app.route("/home")
def home():
    categoryList = crud.getCategories()
    itemList = crud.getAllItems()
    return render_template("home.html", categoryList=categoryList,
                           itemList=itemList, login_session=login_session)


# login page route
@app.route("/login", methods=["GET", "POST"])
def login():
    # generate a random state of 32 characters
    state = "".join(random.choice(
            string.ascii_letters + string.digits)
            for x in range(32))
    login_session["state"] = state

    if request.method == "POST":
        # get login form data
        login_data = request.form

        if login_data["action"] == "LOGIN":
            user_id = crud.getUserID(login_data["loginid"])

            # check for correct password
            # TODO: use bcrypt
            if user_id and crud.getUserPwd(user_id) == login_data["password"]:
                login_session["username"] = login_data["loginid"]
                login_session["user_id"] = user_id
                login_session["provider"] = "database"
                flash("Now logged in as {}".format(login_session["username"]))

        return redirect(url_for("home"))

    return render_template("login.html", STATE=state)


# route for google sign in
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['name'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['password'] = ""
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = crud.getUserIDByEmail(data["email"])
    if not user_id:
        user_id = crud.newUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px;
        height: 300px;
        border-radius: 150px;
        -webkit-border-radius: 150px;
        -moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return jsonify(output={"body": output})


# route for disconnect
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.'))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/logout')
def logout():
    print(login_session)
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            del login_session['provider']
        else:
            if login_session["username"]:
                del login_session["username"]
            if login_session["user_id"]:
                del login_session["user_id"]
            if login_session["provider"]:
                del login_session["provider"]
        flash("You have successfully been logged out.")
        return redirect(url_for('home'))
    else:
        flash("You are not logged in")
        return redirect(url_for('home'))


# route for displaying items in a category
@app.route("/category/<int:id>")
def categoryItems(id):
    categoryList = crud.getCategories()
    itemList = crud.getItemsByCategory(id)
    return render_template("home.html", categoryList=categoryList,
                           itemList=itemList,
                           login_session=login_session,
                           category_id=id)


# route for create new category
# TODO: manage duplicate entries
@app.route("/category/new", methods=["GET", "POST"])
def newCategory():
    # check is user is logged in
    if "username" not in login_session:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = request.form
        if data["action"] == "CREATE":
            cat_data = bleach.clean(data["name"])
            # perform create operation on database
            crud.newCategory(cat_data, login_session["user_id"])
            # flash message to inform user
            flash("New Category {} Created!".format(cat_data))
        return redirect(url_for("home"))
    return render_template("cat_op.html", op="new")


# route for editing a category name
@app.route("/category/<int:id>/edit", methods=["GET", "POST"])
def editCategory(id):
    # check is user is logged in and
    # user owning the category can only edit it
    cat = crud.getCategory(id)
    if "username" not in login_session or\
        cat.user_id != login_session["user_id"]:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = request.form
        if data["action"] == "UPDATE":
            cat_data = bleach.clean(data["name"])
            # perform create operation on database
            crud.editCategory(id, cat_data)
            # flash message to inform user
            flash("Category {} Updated to {}!".format(cat.name, cat_data))
        return redirect(url_for("home"))
    return render_template("cat_op.html", op="edit", cat_name=cat.name)


# route for deleting a category
@app.route("/category/<int:id>/delete", methods=["GET", "POST"])
def deleteCategory(id):
    cat = crud.getCategory(id)
    if "username" not in login_session or \
        cat.user_id != login_session["user_id"]:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = request.form
        if data["action"] == "DELETE":
            # perform create operation on database
            crud.deleteCategory(id)
            # flash message to inform user
            flash("Category {} Deleted!".format(cat.name))
        return redirect(url_for("home"))
    return render_template("cat_op.html", op="delete", cat_name=cat.name)


# route for viewing an item
@app.route("/item/<int:id>/view")
def viewItem(id):
    item = crud.getItemByID(id)
    cat = crud.getCategories()
    return render_template("item_view.html", item=item, categories=cat)


# route for creating a new item
# TODO: manage duplicate entries
@app.route("/item/new", methods=["GET", "POST"])
def newItem():
    cats = crud.getCategories()
    if "username" not in login_session:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = request.form
        if data["action"] == "CREATE":
            name = bleach.clean(data["name"])
            description = bleach.clean(data["description"])
            quantity = bleach.clean(data["quantity"])
            user_id = login_session["user_id"]
            category = int(data["category"])
            # perform create operation on database
            crud.newItem(name, description, quantity, category, user_id)
            # flash message to inform user
            flash("Item {} Created!".format(name))
        return redirect(url_for("home"))
    return render_template("item_op.html", op="new", categories=cats)


# route for editing an item
@app.route("/item/<int:id>/edit", methods=["GET", "POST"])
def editItem(id):
    item = crud.getItemByID(id)
    cats = crud.getCategories()
    if "username" not in login_session or\
        item.user_id != login_session["user_id"]:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = request.form
        if data["action"] == "UPDATE":
            name = bleach.clean(data["name"])
            description = bleach.clean(data["description"])
            quantity = bleach.clean(data["quantity"])
            category = int(data["category"])
            # perform create operation on database
            crud.editItem(id, name, description, quantity, category)
            # flash message to inform user
            flash("Item {} Updated!".format(item.name))
        return redirect(url_for("home"))
    return render_template("item_op.html",
                           op="edit", item=item, categories=cats)


# route for deleting an item
@app.route("/item/<int:id>/delete", methods=["GET", "POST"])
def deleteItem(id):
    item = crud.getItemByID(id)
    if "username" not in login_session or \
        item.user_id != login_session["user_id"]:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = request.form
        if data["action"] == "DELETE":
            # perform create operation on database
            crud.deleteItem(id)
            # flash message to inform user
            flash("Item {} Deleted!".format(item.name))
        return redirect(url_for("home"))
    return render_template("item_op.html", op="delete", item=item)


# route for getting json
@app.route("/json")
def getJSON():
    cats = crud.getCategories()
    items = crud.getAllItems()
    return jsonify(sportsitems=[{
        "id": item.id,
        "name": item.name,
        "category": cats[item.category_id-1].name,
        "category_id":item.category_id,
        "quantity": item.quantity,
        "description": item.description,
    } for item in items])


if __name__ == "__main__":
    # super secure key for flash messaging
    # debug mode
    #app.debug = True
    app.run()