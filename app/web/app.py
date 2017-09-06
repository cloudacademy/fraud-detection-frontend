# encoding:utf-8
from flask import Flask, abort, request 
from flask import render_template
import pymysql
import requests
import json
import os

SERVERFUL_DB_HOST = os.environ['SERVERFUL_DB_HOST']
SERVERFUL_DB_USER = os.environ['SERVERFUL_DB_USER']
SERVERFUL_DB_PASS = os.environ['SERVERFUL_DB_PASS']
SERVERFUL_DB_NAME = os.environ['SERVERFUL_DB_NAME']

SERVERFUL_FRAUDAPI_PREDICT_URL = os.environ['SERVERFUL_FRAUDAPI_PREDICT_URL']

db = pymysql.connect(SERVERFUL_DB_HOST, SERVERFUL_DB_USER, SERVERFUL_DB_PASS, SERVERFUL_DB_NAME, autocommit=True)

app = Flask(__name__)
app.debug = True

@app.route('/', methods=['GET'])
def index():
    cursor = db.cursor()
    sql = "SELECT * FROM testtable"
    cursor.execute(sql)
    results = cursor.fetchall()
    #return render_template('hello.html', name='jeremy1')
    return render_template('index.html', results=results)

@app.route('/health', methods=['GET'])
def health():
    return 'OK'

@app.route('/env1', methods=['GET'])
def env1():
    return SERVERFUL_DB_HOST

@app.route('/env2', methods=['GET'])
def env2():
    return SERVERFUL_DB_USER

@app.route('/env3', methods=['GET'])
def env3():
    return SERVERFUL_DB_PASS

@app.route('/env4', methods=['GET'])
def env4():
    return SERVERFUL_DB_NAME

@app.route('/env5', methods=['GET'])
def env5():
    return SERVERFUL_FRAUDAPI_PREDICT_URL

@app.route('/insert', methods=['POST'])
def insert():
    cursor = db.cursor()
    sql = "INSERT INTO testtable (PersonID, LastName, FirstName, City, Date) VALUES (100, 'Roger', 'Cook', 'Foxton', '2016-05-23 16:12:03.568810')"
    cursor.execute(sql)
    #results = cursor.fetchall()
    #return render_template('hello.html', name='jeremy1')
    return 'OK'

@app.route('/insert2', methods=['POST'])
def insert2():
    PersonID = 400
    LastName = 'McHalick'
    FirstName = 'Olivia'
    City = 'Greytown'
    Date = '2016-05-23 16:12:03.568810'

    cursor = db.cursor()
    sql = "INSERT INTO testtable (PersonID, LastName, FirstName, City, Date) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (PersonID, LastName, FirstName, City, Date))

    return 'OK'

@app.route('/requesttest1', methods=['GET'])
def requesttest1():
    r = requests.get('https://jsonplaceholder.typicode.com/posts/1')
    return r.text

@app.route('/requesttest2', methods=['GET'])
def requesttest2():
    data = {"sender": "Alice", "receiver": "Bob", "message": "We did it!"}
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post('https://jsonplaceholder.typicode.com/posts', data=json.dumps(data), headers=headers)
    return r.text
    
@app.route('/fraud', methods=['POST'])
def fraud():
    if not request.json:
        abort(400)

    return json.dumps(request.json)

@app.route('/fraud2', methods=['POST'])
def fraud2():
    if not request.json:
        abort(400)

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post('https://jsonplaceholder.typicode.com/posts', data=json.dumps(request.json), headers=headers)
    return r.text

@app.route('/fraud3', methods=['POST'])
def fraud3():
    if not request.json:
        abort(400)

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(SERVERFUL_FRAUDAPI_PREDICT_URL, data=json.dumps(request.json), headers=headers)
    data = json.loads(r.text)

    #PersonID = data["id"]
    #LastName = data["LastName"]
    #FirstName = data["FirstName"]
    #City = data["City"]
    #Date = data["Date"]

    LastName = 'Cook'
    FirstName = 'Jeremy'
    CreditCardNumber = '0000111122223333'
    Amount = 125.50
    Score = 0.19899620710890045

    cursor = db.cursor()
    #sql = "INSERT INTO testtable (PersonID, LastName, FirstName, City, Date) VALUES (%s, %s, %s, %s, %s)"
    #cursor.execute(sql, (PersonID, LastName, FirstName, City, Date))
    sql = "INSERT INTO fraud_activity (lastname, firstname, creditcardnumber, amount, score) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (LastName, FirstName, CreditCardNumber, Amount, Score))

    return 'OK'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
