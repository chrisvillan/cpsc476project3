from flask import Flask, jsonify, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash
from sqlite3 import dbapi2 as sqlite3
import time
from hashlib import md5
#cassandra flask from https://github.com/TerbiumLabs/flask-cassandra
from flask_cassandra import CassandraCluster

app = Flask(__name__)
cassandra = CassandraCluster()

app.config['CASSANDRA_NODES'] = ['127.0.0.1']

# configuration
DATABASE = '/tmp/minitwit.db'

PER_PAGE = 30
DEBUG = True
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'


#start - from minitwit.property
# create our little application :)

app = Flask('minitwit')
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

#cassandra

#execute a query. will pick Cass. node to execute
rows = session.execute('SELECT name, age, email FROM users')
for user_row in rows:
    print user_row.name, user_row.age, user_row.email


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'cassandra_db'):
        top.cassandra_db = cassandra.connect()
        top.cassandra_db.set_keyspace('DATABASE')
        top.cassandra_db.row_factory = cassandra.Row
    return top.cassandra_db

@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'cassandra_db'):
        top.cassandra_db.close()

def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.cql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

def populate_db():
    """Repopulates the database."""
    db = cassandra.connect("/tmp/minitwit.db")
    cur = db.cursor()
    cur.execute(
        """
        INSERT INTO mt_db.user(user_id, username, email, password)
        VALUES (%s, %s, %s, %s)
        """,
        (1,"allenapple","allen@gmail.com","passallen")
    )
    cur.execute(
        """
        INSERT INTO mt_db.user(user_id, username, email, password)
        VALUES (%s, %s, %s, %s)
        """,
        (2,"billberry","bill@gmail.com","passbill")
    )
    cur.execute(
        """
        INSERT INTO mt_db.user(user_id, username, email, password)
        VALUES (%s, %s, %s, %s)
        """,
        (3,"codycarrot","cody@gmail.com","passcody")
    )
    cur.execute(
        """
        INSERT INTO mt_db.user(user_id, username, email, password)
        VALUES (%s, %s, %s, %s)
        """,
        (4,"danieldate","daniel@gmail.com","passdaniel")
    )

    db.commit()
    db.close()

@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')

@app.cli.command('populatedb')
def populatedb():
    """Populates the database tables."""
    populate_db()
    print('Repopulates the database.')

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

# followed tutorial series for GET, POST, PUT, DELETE Queries
# https://www.youtube.com/watch?v=CjYKrbq8BCw&list=PLXmMXHVSvS-CoYS177-UvMAQYRfL3fBtX&index=1

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
