from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    flash
)
from functools import wraps
from database_setup import Base, Category, Item, User
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"


# Create session and connect to DB
engine = create_engine('sqlite:///categories-menu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Login Section
# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
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
    except:
        return None


@app.route('/login')
def showLogin():
    """ # Create anti-forgery state token """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is connected'), 200)
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
    # See if user exists
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
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """
    DISCONNECT - Revoke a current user's token and reset their login_session
    """
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for \
given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Categories Information
@app.route('/categories/JSON')
def categoryMenuJSON():
    Menus = session.query(Category).all()
    return jsonify(MenuItems=[i.serialize for i in Menus])


@app.route('/categories/<int:category_id>/items/JSON')
def categoryItemsJSON(category_id):
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(items=[i.serialize for i in items])


@app.route('/categories/<int:category_id>/items/<int:menu_id>/JSON')
def menuItemJSON(category_id, menu_id):
    Menu_Item = session.query(Item).filter_by(id=menu_id).one()
    return jsonify(Menu_Item=[Menu_Item.serialize])


@app.route('/')
@app.route('/category/')
def catMenu():
    """ #Main Page without login """
    cate = session.query(Category).all()
    items = session.query(Item).all()
    if 'username' not in login_session:
        return render_template('categoryMenu.html', cate=cate, items=items)
    else:
        return render_template('addcategoryItem.html', cate=cate, items=items)


@app.route('/categories/<int:category_id>/')
def itemsMenu(category_id):
    """ #Show Category Items without login """
    itemMenu = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=category_id)
    if 'username' not in login_session:
        return render_template('menu.html', itemMenu=itemMenu, items=items)
    else:
        return render_template('menuwithlogin.html', itemMenu=itemMenu,
                               items=items)


@app.route('/item/<int:category_id>/')
def itemShow(category_id):
    items = session.query(Item).all()
    if 'username' not in login_session:
        return render_template('showItem.html', items=items,
                               category_id=category_id)
    else:
        return render_template('show-with-edit-delete.html', items=items,
                               category_id=category_id)


@app.route('/items/new/', methods=['GET', 'POST'])
def newMenuItem():
    """ # Task 1: Create route for newItem function here """
    itemMenu = session.query(Category).all()
    if 'username' not in login_session:
        return redirect('/login')
    else:
        if request.method == 'POST':
            newItem = Item(name=request.form['name'],
                           description=request.form['description'],
                           category_id=request.form['category'],
                           user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
            return redirect(url_for('catMenu'))
        else:
            return render_template('newmenuitem.html', itemMenu=itemMenu)


@app.route('/category/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    """ # Task 2 : Create route for editItem function here """
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    else:
        # Get all categories
        categories = session.query(Category).all()
        # Get category item
        categoryItem = session.query(Item).filter_by(id=item_id).first()
        # Get creator of item
        creator = getUserInfo(categoryItem.user_id)
        # Check if logged in user is creator of category item
        if creator.id != login_session['user_id']:
            return redirect('/login')
        if request.method == 'POST':
            if request.form['name']:
                categoryItem.name = request.form['name']
            if request.form['description']:
                categoryItem.description = request.form['description']
            if request.form['category']:
                categoryItem.category_id = request.form['category']
            session.add(categoryItem)
            session.commit()
            return redirect(url_for('itemShow', category_id=categoryItem.id))
        else:
            return render_template('editCategoryItem.html',
                                   categories=categories,
                                   categoryItem=categoryItem,
                                   category_id=category_id,
                                   item_id=item_id)


@app.route('/catalog/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    """ # Task 3 : Create route for deleteItem function here """
    # Check if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    else:
        # Get category item
        categoryItem = session.query(Item).filter_by(id=item_id).first()
        # Get creator of item
        creator = getUserInfo(categoryItem.user_id)
        # Check if logged in user is creator of category item
        if creator.id != login_session['user_id']:
            return redirect('/login')
        if request.method == 'POST':
            session.delete(categoryItem)
            session.commit()
            return redirect(url_for('itemsMenu',
                                    category_id=categoryItem.category_id))
        else:
            return render_template('deleteCategoryItem.html',
                                   category_id=category_id,
                                   item_id=item_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
