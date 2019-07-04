import sqlite3
import datetime
from flask import Flask, render_template, g, request, redirect, url_for

# Path to the project's DB
PATH='db/jobs.sqlite'

app = Flask(__name__)

# This establishes a connection with the SQlite DB
def open_connection(db_path):
    connection = getattr(g, '_connection', None)
    if connection == None:
        connection = g._connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection

# Creates a new DB entry
def execute_sql(sql, values=(), commit=False, single=False):
        connection = open_connection(PATH)
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
    reviews = execute_sql('SELECT review, rating, title, date, status FROM review JOIN employer ON employer.id = review.employer_id WHERE employer.id = ?', [employer_id])
    return render_template('employer.html', employer = employer, jobs = jobs, reviews = reviews)

@app.route('/employer/<employer_id>/review_new', methods = {'GET', 'POST', 'DELETE'})
def review_new(employer_id):
    # This is to handle the POST request (to enter a new review for the employer)
    if request.method == 'POST':
        review = request.form['review']
        rating = request.form['rating']
        title = request.form['title']
        status = request.form['status']

        date  = datetime.datetime.now().strftime("%m/%d/%Y")

        execute_sql('INSERT INTO review (review, rating, title, date, status, employer_id) VALUES (?, ?, ?, ?, ?, ?)', (review, rating, title, date, status, employer_id), commit = True)

        return redirect( url_for('employer', employer_id = employer_id) )

    # Self improvised part
    # else if request.method == 'DELETE':

    # This will show all reviews for one employer
    return render_template('review_new.html', employer_id = employer_id)

# Self improvised functions
@app.route('/employer/<employer_id>/job_new', methods = {'GET', 'POST', 'DELETE'})
def job_new(employer_id):
    if request.method == 'POST':
        title = request.form['title']
        salary = request.form['salary']
        description = request.form['description']

        execute_sql('INSERT INTO job (title, description, salary, employer_id) VALUES (?, ?, ?, ?)', (title, description, salary, employer_id), commit = True)

        return redirect( url_for('employer', employer_id =  employer_id) )

    return render_template('job_new.html', employer_id = employer_id)
