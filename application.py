from flask import Flask, render_template, request, redirect
from flask import url_for, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Department, DepartmentItem, User

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from oauth2client import client
from apiclient import discovery
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Grocery Catalog'

engine = create_engine(
    'sqlite:///supermarketitems.db',
    connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
      Function to validate Google connect
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user already connected'),
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
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists , if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' "style = "width: 300px; height: 300px;border-radius: 150px;'\
        '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
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
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# logout
@app.route('/logout')
def logout():
    gdisconnect()
    del login_session['access_token']
    del login_session['gplus_id']

    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']

    return redirect(url_for('showCategoreis'))


# provide json endpoint
@app.route('/catalogs/JSON')
def catalogJSON():
    categories = session.query(Department).all()
    return jsonify(Categories=[c.serialize for c in categories])


@app.route('/catalogs/<int:cata_id>/items/JSON')
def categoryJSON(cata_id):
    department = session.query(Department).filter_by(id=cata_id).one()
    items = session.query(DepartmentItem).filter_by(
        department_id=department.id)
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalogs/<int:cata_id>/items/<int:item_id>/JSON')
def itemJSON(cata_id, item_id):
    item = session.query(DepartmentItem).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


@app.route('/')
@app.route('/catalogs')
def showCategoreis():
    departments = session.query(Department).all()
    items = session.query(DepartmentItem).all()
    if 'username' not in login_session:
        return render_template(
            'public_catalogs.html',
            catalogs=departments,
            items=items)
    else:
        return render_template(
            'catalogs.html',
            catalogs=departments,
            items=items)


@app.route('/catalogs/new', methods=['GET', 'POST'])
def newItem():
    if 'username' not in login_session:
        return redirect('/login')
    departments = session.query(Department).all()
    if request.method == 'POST':
        newItem = DepartmentItem(
            name=request.form['name'],
            price=request.form['price'],
            description=request.form['description'],
            department_id=request.form['department'],
            user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Item Successfully Added')
        return redirect(url_for('showCategoreis'))
    else:
        return render_template(
            'newCatalogsItem.html', departments=departments)


# view items in a department
@app.route('/catalogs/<int:cata_id>')
@app.route('/catalogs/<int:cata_id>/items')
def showCatalogsItem(cata_id):
    departments = session.query(Department).all()
    department = session.query(Department).filter_by(id=cata_id).one()
    items = session.query(DepartmentItem).filter_by(
        department_id=department.id)
    return render_template(
        'cataItem.html',
        catalogs=departments,
        catalog=department,
        items=items)


@app.route('/catalogs/<int:cata_id>/items/<int:item_id>/')
def showOneItem(cata_id, item_id):
    department = session.query(Department).filter_by(id=cata_id).one()
    item = session.query(DepartmentItem).filter_by(id=item_id).one()
    return render_template(
        'item.html',
        catalog=department.name,
        cata_id=cata_id,
        item=item)


# edit an item
@app.route(
    '/catalogs/<int:cata_id>/items/<int:item_id>/edit',
    methods=['GET', 'POST'])
def editItem(cata_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    departments = session.query(Department).all()
    editedItem = session.query(DepartmentItem).filter_by(id=item_id).one()
    if login_session['user_id'] != editedItem.user_id:
        flash('You can only edit items added by yourself')
        return redirect(url_for('showCategoreis'))
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['department']:
            editedItem.department_id = request.form['department']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        flash('Item Successfully Edited')
        return redirect(url_for('showCategoreis'))
    else:
        return render_template(
            'editItem.html',
            cata_id=cata_id,
            item_id=item_id,
            departments=departments,
            item=editedItem)


# delete an item
@app.route(
    '/catalogs/<int:cata_id>/items/<int:item_id>/delete',
    methods=['GET', 'POST'])
def deleteCatalogsItem(cata_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    deletedItem = session.query(DepartmentItem).filter_by(id=item_id).one()
    if login_session['user_id'] != deletedItem.user_id:
        flash('You can only delete items added by yourself')
        return redirect(url_for('showCategoreis'))
    if request.method == 'POST':
        session.delete(deletedItem)
        session.commit()
        flash('Item Successfully Deleted')
        return redirect(url_for('showCategoreis'))
    else:
        return render_template(
            'deleteCatalogsItem.html',
            item=deletedItem, cata_id=cata_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
