from flask import Flask, jsonify, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash
from sqlite3 import dbapi2 as sqlite3
import time
from hashlib import md5
app = Flask(__name__)

# followed tutorial series for GET, POST, PUT, DELETE Queries
# https://www.youtube.com/watch?v=CjYKrbq8BCw&list=PLXmMXHVSvS-CoYS177-UvMAQYRfL3fBtX&index=1


# configuration
# still need to change to a new API-_BASE_URL setting
DATABASE = '/tmp/minitwit.db'

PER_PAGE = 30
DEBUG = True
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'


#start - from minitwit.property
# create our little application :)
app = Flask('minitwit')
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
        top.sqlite_db.row_factory = sqlite3.Row
    return top.sqlite_db

@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()

def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

@app.cli.command()
def populatedb():
    """Repopulates the database."""
    db = sqlite3.connect("/tmp/minitwit.db")
    cur = db.cursor()
    cur.execute("INSERT INTO user(username,email,pw_hash) VALUES (user1, user1email, test1)", (username, email, pw_hash))
    db.commit()
    db.close()
    print('Repopulate the database.')

def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('select user_id from user where username = ?',
                  [username], one=True)
    return rv[0] if rv else None

#end - from minitwit.property

#having a hard time repopulating data base from population.sql. So for now, I'm hard coding it
users = [{
            'name' : 'amy',
            'email' : 'amy@ecs.com',
            'message' : 'hi my name is amy'
            }, {
            'name' : 'bill',
            'email': 'bill@ecs.com',
            'message' : 'hi my name is bill'
            }, {
            'name' : 'carrie',
            'email': 'carrie@ecs.com',
            'message' : 'hi my name is carrie'
            }]


@app.route('/', methods=['GET'])
def test():
    return jsonify({'message' : 'Message works!'})

@app.route('/users', methods=['GET'])
def returnALL():
    return jsonify({'users':users})

@app.route('/users/<string:name>', methods=['GET'])
def returnOne(name):
    usrs = [user for user in users if user['name'] == name]
    return jsonify({'user': usrs[0]})

@app.route('/users', methods = ['POST'])
def addOne():
    user = {'name' : request.json['name'], 'email' : request.json['email'], 'message' : request.json['message']}

    users.append(user)
    return jsonify({'users' : users})

@app.route('/usr/<string:name>', methods = ['PUT'])
def editOne(name):
    usrs = [user for user in users if user['name'] == name]
    usrs[0]['name'] = request.json['name']
    return jsonify({ 'user' : usrs[0]})

@app.route('/usr/<string:name>', methods = ['DELETE'])
def removeOne(name):
    usr = [user for user in users if user['name'] == name]
    users.remove(usr[0])
    return jsonify({ 'users' : users})

if __name__=='__main__':
    app.run(debug=True)
