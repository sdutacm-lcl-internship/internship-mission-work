import json
import time

import pytz
import sqlite3
import requests
import datetime
from fake_useragent import UserAgent
from flask import Flask, request, Response, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333, debug=True)




