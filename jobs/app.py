import sqlite3
from flask import Flask, render_template, g

# Path to the project's DB
PATH='db/jobs.sqlite'

app = Flask(__name__)

# This establishes a connection with the SQlite DB
def open_connection():
    connection = getattr(g, '_connection', None)
    if connection == None:
        connection = g._connection = sqlite3.connect(PATH)
    connection.row_factory = sqlite3.Row
    return connection

# Creates a new DB entry
def execute_sql(sql, values=(), commit=False, single=False):
        connection = open_connection()
        cursor = connection.execute(sql, values)
        if commit == True:
            results = connection.commit()
        else:
            results = cursor.fetchone() if single else cursor.fetchall()

        cursor.close()
        return results

# This will close the connection to the SQlite3
# The decorator ensure the connection to the DB is closed when the app process is "destroyed"
@app.teardown_appcontext
def close_connection(exception):
    connection = getattr(g, '_connection', None)
    if connection is not None:
        connection.close()

@app.route('/')
@app.route('/jobs')
def jobs():
    return render_template('index.html')
