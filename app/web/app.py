# encoding:utf-8
from flask import Flask, abort, request, jsonify 
from flask import render_template
from flask import make_response
from flask_cors import CORS, cross_origin
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

#cors = CORS(app, resources={"/*": {"origins": "*"}})
cors = CORS(app)

@app.route('/version', methods=['GET'])
def version():
    return '1.5'
    
@app.route('/fraudreport', methods=['GET'])
def fraudreport():
    cursor = db.cursor()
    sql = "SELECT * FROM fraud_activity"
    cursor.execute(sql)
    results = cursor.fetchall()
    r = make_response(render_template('index.html', results=results))
    r.headers.set('Content-Type', 'text/html')
    return r

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

@app.route('/fraudpredict', methods=['POST'])
def fraudpredict():
    if not request.json:
        abort(400)

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(SERVERFUL_FRAUDAPI_PREDICT_URL, data=json.dumps(request.json), headers=headers)
    data = json.loads(r.text)

    for index, score in enumerate(data["scores"], start=0):
        LastName = 'Cook'
        FirstName = 'Bob'
        CreditCardNumber = '0000111122223333'
        Amount = request.json["features"][index][29]
        ScoreRounded = '{:.10f}'.format(round(score, 10))
        ScoreString = repr(score)

        try:
            cursor = db.cursor()
            sql = "INSERT INTO fraud_activity (lastname, firstname, creditcardnumber, amount, score, scoredetail) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (LastName, FirstName, CreditCardNumber, Amount, ScoreRounded, ScoreString))
        except:
            app.logger.info('error: %s, %s, %s, %s, %s, %s, %s' % (LastName, FirstName, CreditCardNumber, Amount, ScoreRounded, ScoreString, score))


    result = jsonify({"result": 'ok'})
    return result

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
