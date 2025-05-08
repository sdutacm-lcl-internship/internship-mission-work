from flask import Flask,request,jsonify,Response,render_template,make_response
from datetime import timedelta, datetime
import flask
import time,os
import sqlite3
import pytz
import requests
import json
import re
import sys

app = Flask(__name__)

map_user = {}
map_rating = {}

status_codes = 0

def sqlite_user_info(handle, rating, rank):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        now = datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO user_info(handle,rating,rank,updated_at)
            VALUES(?,?,?,?)
            ''', (handle, rating, rank, now))
        conn.commit()


def sqlite_user_rating(handle, contestId, contestName, rank, oldRating, newRating, ratingUpdatedAt):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        now = datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()
        cursor.execute("SELECT handle FROM user_info WHERE handle = ?", (handle,))
        data = cursor.fetchone()
        if data is None:
            get_ansjson(handle)
        cursor.execute('''
            INSERT OR REPLACE INTO user_ratings(handle,contest_id,contest_name,rank,old_rating,new_rating,rating_updated_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?)
            ''', (handle, contestId, contestName, rank, oldRating, newRating, ratingUpdatedAt, now))
        conn.commit()


def get_ansjson(name):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT rating,rank FROM user_info
            WHERE handle = ? AND updated_at > ?
            ''', (name, (datetime.now(pytz.timezone('Asia/Shanghai')) - timedelta(seconds=30)).isoformat()))
        row = cursor.fetchone()
        if row:
            rating, rank = row
            if rating and rank:
                result = {
                    'handle': name,
                    'rating': rating,
                    'rank': rank
                }
            else:
                result = {
                    'handle': name
                }
            data = {
               'success': True,
               'result': result
            }
            return data

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36 Edg/122.0.0.0'
    }
    param = {
        "handles": name
    }
    try:
        response = requests.get("https://codeforces.com/api/user.info", headers=headers, params=param)
        status_code = response.status_code
        if status_code == 200:
            res_json = json.loads(response.text)
            user_data = res_json['result'][0]
            #情况1：成功找到用户名
            if 'rating' in user_data:
                data = {
                    'success': True,
                    'result': {
                        'handle': user_data['handle'],
                        'rating': int(user_data['rating']),
                        'rank': user_data['rank']
                    }
                }
                sqlite_user_info(user_data['handle'],int(user_data['rating']), user_data['rank'])
            elif 'handle' in user_data:
                data = {
                    'success': True,
                    'result': {
                        'handle': user_data['handle']
                    }
                }
            # map_user[name] = {
            #     'data': data,
            #     'pop': datetime.now() + timedelta(seconds=15)
            # }
            #json_data = json.dumps(ans)
            #sys.stdout.write(json_data + '\n')
        #情况2：未找到用户名
        elif status_code == 400:
            data = {
                'success': False,
                'type': 1,
                'message': 'no such handle'
            }
        #情况3：http响应错误
        else:
            data = {
                'success': False,
                'type': 2,
                'message': 'HTTP response with code {}'.format(status_code),
                'details': {
                    'status': status_code
                }
            }
        # map_user[name] = {
        #     'data': data,
        #     'pop': datetime.now() + timedelta(seconds=15)
        # }
    #情况4：未得到有效响应（连接错误）
    except requests.exceptions.ConnectionError as e:
        return {
            'success': False,
            'type': 3,
            'message': 'Request timeout',
        }
    #情况4：未得到有效相应（连接错误）
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'type': 3,
            'message': 'Request timeout',
        }
    #情况5：程序本身错误
    except :
        return {
            'success': False,
            'type': 4,
            'message': 'Internal Server Error'
        }
    conn.close()
    status_codes=status_code
    return data

def get_resjson(name):

    # if name in map_rating and map_rating[name]['pop'] > datetime.now():
    #     return map_rating[name]['data']
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT contest_id,contest_name,rank,old_rating,new_rating,rating_updated_at FROM user_ratings
            WHERE handle = ? AND updated_at > ?
            ''', (name, (datetime.now(pytz.timezone('Asia/Shanghai')) - timedelta(seconds=30)).isoformat()))
        rows = cursor.fetchall()
        if rows:
            data = []
            for row in rows:
                contest_id, contest_name, rank, oldrating, newrating, ratingUpdatedAt = row
                data.append({
                    'handle': name,
                    'contestId': contest_id,
                    'contestName': contest_name,
                    'rank': rank,
                    'ratingUpdatedAt': ratingUpdatedAt,
                    'oldRating': oldrating,
                    'newRating': newrating
                })
            return data

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36 Edg/122.0.0.0'
    }
    param = {
        "handles": name
    }
    ans = {}
    try:
        response = requests.get(f"https://codeforces.com/api/user.rating?handle={name}", headers=headers, params=param)
        res_json = response.json()
        status_code = response.status_code
        status_end_code = status_code
        res = []
        if status_code == 200:
            res_json = json.loads(response.text)
            user_data = res_json['result']
            # 情况1：成功找到用户名
            for user_info in user_data:
                ratingUpdateTimeSeconds = user_info['ratingUpdateTimeSeconds']
                time = datetime.fromtimestamp(ratingUpdateTimeSeconds, pytz.timezone('Asia/Shanghai'))
                ratingUpdatedAt = time.isoformat()
                res.append( {
                    'handle': user_info['handle'],
                    'contestId': user_info['contestId'],
                    'contestName': user_info['contestName'],
                    'rank': int(user_info['rank']),
                    'ratingUpdatedAt': ratingUpdatedAt,
                    'oldRating': int(user_info['oldRating']),
                    'newRating': int(user_info['newRating'])
                })
                sqlite_user_rating(user_info['handle'], user_info['contestId'], user_info['contestName'], int(user_info['rank']), int(user_info['oldRating']), int(user_info['newRating']), ratingUpdatedAt)
            conn.close()
            # json_data = json.dumps(ans)
            # sys.stdout.write(json_data + '\n')
        # 情况2：未找到用户名
        elif status_code == 400:
            status_end_code = 404
            res = {
                'message': 'no such handle',
                'status': 404
            }
        # 情况3：http响应错误
        else:
            status_end_code = status_code
            res = {
                'message': 'HTTP response with code {}'.format(status_code),
                'status': status_code
            }
        # map_rating[name] = {
        #     'data': res,
        #     'pop': datetime.now() + timedelta(seconds=30)
        # }
    # 情况4：未得到有效响应（无网络链接）
    except requests.exceptions.ConnectionError as e:
        status_end_code = 500
        return {
            'message': 'Internal Server Error',
            'status': 500
        }
    # 情况4： 未得到有效响应（无网络链接）
    except requests.exceptions.RequestException as e:
        status_end_code = 500
        return {
            'message': 'Request timeout',
            'status': 500
        }
    #情况5：程序本身错误
    except :
        return {
            'success': False,
            'type': 4,
            'message': 'Internal Server Error'
        }
    status_codes=status_code
    return res

@app.route('/batchGetUserInfo')
def get_handles():
    handles = request.args.get('handles').split(',')
    results = []
    for handle in handles:
        result = get_ansjson(handle)
        results.append(result)
    return Response(json.dumps(results), mimetype='application/json')


@app.route('/getUserRatings')
def get_Ratings():
    handle = request.args.get('handle')
    results = []
    # results = get_resjson(handle)
    results = get_resjson(handle)
    if 'message' in results and 'status' in results:
        response = make_response(json.dumps(results),results['status'])
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(results), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # return Response(json.dumps(results), mimetype='application/json')

@app.route('/', methods=['get', 'post'])
def get_rating_html():
    return render_template('index.html')

def creat():
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_info (
                handle VARCHAR PRIMARY KEY NOT NULL,
                rating INT,
                rank VARCHAR,
                updated_at DATETIME NOT NULL
            )
        ''')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_ratings(
                        user_rating_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        handle VARCHAR NOT NULL,
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

if __name__ == '__main__':
    creat()
    app.run(host='127.0.0.1', port=2333, debug=True)


