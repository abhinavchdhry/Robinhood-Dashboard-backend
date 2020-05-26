from flask import Flask, request
from flask_cors import CORS
import csv
import json

app = Flask(__name__)
CORS(app)

def verify_credentials(username, password):
    return True

def get_session_for_user(username):
    return 'afj8augja0v0aga'

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = 'ERROR'
    if request.method == 'POST':
        if verify_credentials(request.form['username'], request.form['password']):
            return get_session_for_user(request.form['username'])
        else:
            error = 'Invalid username/password'

    return error

def load_data():
    data = []
    f = open('robinhood.csv', 'r')
    csvreader = csv.DictReader(f, delimiter='|')
    for row in csvreader:
        data.append(row)
    return data

@app.route('/trades', methods=['GET'])
def get_trades():
    data = load_data()
    return json.dumps(data, indent=2)


def _get_trade_volume(by='day'):
    data = load_data()

    map(lambda t: (t['last_transaction_time'], t['average_price'], t['cumulative_quantity'], t['state']), data)

@app.route('/trade_volume', methods=['POST'])
def get_trade_volume():
    error = "ERROR"
    if request.method == 'POST':
        aggregate_by = request.form['by']
        return _get_trade_volume(aggregate_by)

    return error

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
