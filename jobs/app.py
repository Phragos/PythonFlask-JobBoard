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

# The decorator are to specify which path requests this function
@app.route('/')
@app.route('/jobs')
def jobs():
    # Runs a SQL query on tables job and employer and assigns the result to jobs
    jobs = execute_sql('SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id')
    # This calls the template that will be returned, and passes the parameter for the jobs to be generated
    return render_template('index.html', jobs = jobs)

# This decorator specifies the path and includes a path variable job_id that can be used in the function
@app.route('/job/<job_id>')
def job(job_id):
    job = execute_sql('SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id WHERE job.id = ?', [job_id], single = True)
    return render_template('job.html', job = job)

@app.route('/employer/<employer_id>')
def employer(employer_id):
    employer = execute_sql('SELECT * FROM employer WHERE id = ?', [employer_id], single = True)
    jobs = execute_sql('SELECT job.id, job.title, job.description, job.salary FROM job JOIN employer ON employer.id = job.employer_id WHERE employer.id = ?', [employer_id])
    review = execute_sql('SELECT review, rating, title, date, status FROM review JOIN employer ON employer.id = review.employer_id WHERE employer.id = ?', [employer_id])
    return render_template('employer.html', employer = employer, jobs = jobs, review = review)
