import flask
import sqlite3
from flask import Flask, request, Response, make_response, render_template
import requests
import json
from datetime import timedelta, datetime
import pytz
import query

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['DEBUG'] = True

app.jinja_env.variable_start_string = '<<'  # 解决与vue 标签的冲突
app.jinja_env.variable_end_string = '>>'


def update_info(handle, rating, rank):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        now = datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()
        cursor.execute(
            '''
        INSERT OR REPLACE INTO user_info(handle,rating,rank,updated_at)
        VALUES(?,?,?,?)
        ''', (handle, rating, rank, now))
        conn.commit()


def update_rating(handle, contest_id, contest_name, rank, old_rating,
                  new_rating, ratingUpdatedAt):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        now = datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()
        cursor.execute("SELECT handle FROM user_info WHERE handle = ?",
                       (handle, ))
        data = cursor.fetchone()
        if data is None:
            query.get_user_info(handle)
        cursor.execute(
            '''
                    INSERT OR REPLACE INTO user_ratings(handle,contest_id,contest_name,rank,old_rating,new_rating,rating_updated_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?)
            ''', (handle, contest_id, contest_name, rank, old_rating,
                  new_rating, ratingUpdatedAt, now))
        conn.commit()


@app.route('/batchGetUserInfo')
def URL_handles():
    handles = request.args.get('handles', '').split(',')
    results = []
    for handle in handles:
        result = query.get_user_info(handle)
        results.append(result)
    return Response(json.dumps(results), mimetype='application/json')


@app.route('/getUserRatings')
def URL_ratings():
    handle = request.args.get('handle', '')
    results = []
    results = query.get_user_rating(handle)
    if 'message' in results and 'code' in results:
        result = {'message': results['message']}
        response = make_response(json.dumps(result), results['code'])
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        if 'message' in results:
            response = make_response(json.dumps(results), 404)
            response.headers['Content-Type'] = 'application/json'
            return response

        response = make_response(json.dumps(results), 200)
        response.headers['Content-Type'] = 'application/json'
        return response


def creat_db():
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_info (
                 handle VARCHAR PRIMARY KEY NOT NULL COLLATE NOCASE,
                rating INT,
                rank VARCHAR,
                updated_at DATETIME NOT NULL
            )
        ''')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_ratings(
                        user_rating_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        handle VARCHAR NOT NULL COLLATE NOCASE,
                        contest_id INT NOT NULL,
                        contest_name VARCHAR NOT NULL,
                        rank INT NOT NULL,
                        old_rating INT NOT NULL,
                        new_rating INT NOT NULL,
                        rating_updated_at DATETIME NOT NULL,
                        updated_at DATETIME NOT NULL,
                        FOREIGN KEY (handle) REFERENCES user_info (handle),
                        UNIQUE(handle, contest_id) ON CONFLICT REPLACE
                    );
                ''')
    conn.commit()


@app.route('/', methods=['GET'])
def yuanshenzenmonile():
    return render_template('query.html')


if __name__ == '__main__':
    creat_db()
    app.run(host='127.0.0.1', port=2333, debug=True)
