# encoding:utf-8
from flask import Flask, abort, request, jsonify 
from flask import render_template
from flask import make_response
from flask_cors import CORS, cross_origin
import pymysql
import requests
import json
import os
import subprocess

SERVERFUL_DB_HOST = os.environ['SERVERFUL_DB_HOST']
SERVERFUL_DB_USER = os.environ['SERVERFUL_DB_USER']
SERVERFUL_DB_PASS = os.environ['SERVERFUL_DB_PASS']
SERVERFUL_DB_NAME = os.environ['SERVERFUL_DB_NAME']

SERVERFUL_FRAUDAPI_PREDICT_URL = os.environ['SERVERFUL_FRAUDAPI_PREDICT_URL']
    
db = pymysql.connect(SERVERFUL_DB_HOST, SERVERFUL_DB_USER, SERVERFUL_DB_PASS, SERVERFUL_DB_NAME, autocommit=True)

app = Flask(__name__)
app.debug = True

cors = CORS(app)

CLUSTER_INSTANCE_IP = ''
DOCKER_CONTAINER_HOSTNAME = ''
DOCKER_CONTAINER_IP = ''

try:
    DOCKER_CONTAINER_HOSTNAME = subprocess.check_output("hostname", shell=True)
    app.logger.info('DOCKER_CONTAINER_HOSTNAME: %s' % (DOCKER_CONTAINER_HOSTNAME))
except:
    app.logger.info('problem querying docker container hostname')

try:
    DOCKER_CONTAINER_IP = subprocess.check_output("hostname -i", shell=True)
    app.logger.info('DOCKER_CONTAINER_IP: %s' % (DOCKER_CONTAINER_IP))
except:
    app.logger.info('problem querying docker container ip address')

try:
    metadata_request = requests.get('http://169.254.169.254/latest/meta-data/local-ipv4/')
    CLUSTER_INSTANCE_IP = metadata_request.text
    app.logger.info('CLUSTER_INSTANCE_IP: %s' % (CLUSTER_INSTANCE_IP))
except:
    app.logger.info('problem connecting to ec2 metadata')

@app.route('/health', methods=['GET'])
def health():
    return 'OK'

@app.route('/env/1', methods=['GET'])
def env1():
    return SERVERFUL_DB_HOST

@app.route('/env/2', methods=['GET'])
def env2():
    return SERVERFUL_DB_USER

@app.route('/env/3', methods=['GET'])
def env3():
    return SERVERFUL_DB_PASS

@app.route('/env/4', methods=['GET'])
def env4():
    return SERVERFUL_DB_NAME

@app.route('/env/5', methods=['GET'])
def env5():
    return SERVERFUL_FRAUDAPI_PREDICT_URL

@app.route('/docker/container/hostname', methods=['GET'])
def dockerhost():
    return DOCKER_CONTAINER_HOSTNAME

@app.route('/docker/container/ip', methods=['GET'])
def dockerip():
    return DOCKER_CONTAINER_IP

@app.route('/cluster/instance/ip', methods=['GET'])
def clusterinstanceip():
    return CLUSTER_INSTANCE_IP

@app.route('/fraud/report', methods=['GET'])
def fraudreport():
    cursor = db.cursor()
    sql = "SELECT * FROM fraud_activity"
    cursor.execute(sql)
    results = cursor.fetchall()
    r = make_response(render_template('index.html', results=results))
    r.headers.set('Content-Type', 'text/html')
    return r

@app.route('/fraud/predict', methods=['POST'])
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
        ScoreString = repr(score)

        try:
            cursor = db.cursor()
            sql = "INSERT INTO fraud_activity (lastname, firstname, creditcardnumber, amount, score, scoredetail) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (LastName, FirstName, CreditCardNumber, Amount, score, ScoreString))
        except Exception as e:
            app.logger.info('data: %s' % (data))
            app.logger.info('error: %s, %s, %s' % (Amount, ScoreString, score))
            app.logger.info(e.__doc__)
            app.logger.info(e.message)

    result = jsonify({"result": 'ok'})
    return result

@app.route('/version', methods=['GET'])
def version():
    return '2.4'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
