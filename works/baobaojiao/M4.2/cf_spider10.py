import requests
import datetime
import time
import pytz
import sqlite3
from flask import Flask, jsonify, request, Response
from gevent import pywsgi
from flask import render_template
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

cache_userinfo = {}
cache_userrating = {}


def convert_to_unix(time_str):
    dt = datetime.datetime.fromisoformat(time_str)

    utc_dt = dt.astimezone(datetime.timezone.utc)

    unix_time = int((utc_dt - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds())

    return unix_time


def unix_to_iso(unix_time):
    Date_Time = datetime.datetime.fromtimestamp(unix_time, pytz.timezone('Asia/Shanghai'))  # 转换Unix时间戳
    Iso_Time = Date_Time.isoformat()  # 转换为iso
    return Iso_Time


def unix_to_datetime(unix_time):
    dt = datetime.datetime.fromtimestamp(unix_time)
    dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
    return dt_str


def datetime_to_unix(datetime_str):
    datetime_obj = datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    unix_timestamp = datetime_obj.timestamp()
    return int(unix_timestamp)


def grep_user(user):
    url = 'https://codeforces.com/api/user.info'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 Edg/113.0.1774.42'
    }

    param = {
        "handles": user
    }

    try:  # 程序正常运行
        response = requests.get(url=url, headers=headers, params=param)
        page = response.json()
        resp_status_code = response.status_code

        if resp_status_code == 200:  # 请求发送正常
            if 'rating' in page['result'][0]:
                ans = {
                    'sucess': 'true',
                    'result': {"handle": user,
                               "rating": page['result'][0]['rating'],
                               "rank": page['result'][0]['rank'],
                               },
                    'updated_at': unix_to_datetime(time.time())
                }
            else:
                ans = {
                    'sucess': 'true',
                    'result': {
                        "handle": user
                    },
                    'updated_at': unix_to_datetime(time.time())
                }
            return ans, 200
        elif page['status'] == "FAILED":
            ans = {
                "success": "false",
                "type": 1,
                "message": "no such handle"
            }
            return ans, 404
        elif resp_status_code == 401 or resp_status_code == 403 or resp_status_code == 404 or resp_status_code == 500 or resp_status_code == 502 or resp_status_code == 503 or resp_status_code == 504:
            # 请求响应异常
            ans = {
                "success": 'false',
                "type": '2',
                "message": "HTTP response with code" + str(resp_status_code),
                "details": {
                    "status": str(resp_status_code)
                }
            }
            return ans, resp_status_code
        else:  # 除去响应异常以及程序异常，剩下的为未收到合法响应
            ans = {
                "success": 'false',
                "type": '3',
                "message": "No valid HTTP response was received when querying this item"
            }
            return ans, 400
    except requests.exceptions.RequestException as e:  # 程序抛出异常
        ans = {
            "success": 'false',
            "type": '3',
            "message": "Internal Server Error"
        }
        return ans, 500
    except Exception as e:
        ans = {
            "success": "false",
            "type": "4",
            "message": 'Internal Server Error'
        }
        return ans, 500


def grep_rating(handle):
    url = 'https://codeforces.com/api/user.rating'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 Edg/113.0.1774.42'
    }

    param = {
        "handle": handle
    }

    try:
        response = requests.get(url=url, headers=headers, params=param)
        page = response.json()
        resp_status = response.status_code
        status_code = resp_status

        res = []
        ans = {}
        if resp_status == 200:
            for rating_info in page['result']:
                temp = {
                    "handle": rating_info['handle'],
                    "contestId": rating_info['contestId'],
                    "contestName": rating_info['contestName'],
                    "rank": rating_info['rank'],
                    "ratingUpdatedAt": unix_to_iso(rating_info['ratingUpdateTimeSeconds']),
                    "oldRating": rating_info['oldRating'],
                    'newRating': rating_info['newRating']
                }
                res.append(temp)
            ans = {
                'handle': handle,
                'updated_at': unix_to_datetime(time.time()),
                'result': res
            }
        elif resp_status == 400:
            status_code = 404
            ans = {
                "message": "no such handle"
            }
        elif resp_status == 401 or resp_status == 403 or resp_status == 404 or resp_status == 500 or resp_status == 502 or resp_status == 503 or resp_status == 504:
            status_code = resp_status,
            ans = {
                "message": "HTTP response with code" + str(resp_status)
            }
    except requests.exceptions.RequestException as e:  # 程序抛出异常
        status_code = 500
        ans = {
            "message": "Internal Server Error"
        }
    except Exception as e:
        status_code = 500
        ans = {
            "message": "Internal Server Error"
        }
    return ans, status_code


def init_database():
    try:
        conn = sqlite3.connect('cf.db')
        cursor = conn.cursor()
        # user表
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS user_info (
        handle VARCHAR PRIMARY KEY NOT NULL,
        rating INT,
        rank VARCHAR,
        updated_at DATETIME NOT NULL
               )
        '''
        cursor.execute(create_table_query)
        conn.commit()

        # rating表
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS user_rating(
        user_rating_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        handle VARCHAR NOT NULL,
        contest_id INT NOT NULL,
        contest_name VARCHAR NOT NULL,
        rank INT NOT NULL,
        old_rating INT NOT NULL,
        new_rating INT NOT NULL,
        rating_updated_at NOT NULL,
        updated_at DATETIME NOT NULL,
        FOREIGN KEY (handle) REFERENCES user_info(handle)
        )
        '''
        cursor.execute(create_table_query)
        conn.commit()
        conn.close()
    except Exception as e:
        return {'message': 'nternal Server Error'}, 500
    return {'message': 'ok'}, 200


def get_userinfo_from_database(handles):
    ans = []
    try:
        conn = sqlite3.connect('cf.db')
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        for handle in handles:
            sql = "SELECT * FROM user_info WHERE handle = ?"
            handle = handle
            cursor.execute(sql, (handle,))
            result = cursor.fetchall()
            if len(result) == 0:
                res = grep_user(handle)
                if res[1] != 200:
                    ans.append(res[0])
                    continue
                if 'rating' in res[0]['result']:
                    sql = "INSERT INTO user_info (handle, rating, rank, updated_at) VALUES(?, ?, ?, ?)"
                    cursor.execute(sql, (
                    res[0]['result']['handle'], res[0]['result']['rating'], res[0]['result']['rank'],
                    res[0]['updated_at']))
                else:
                    sql = "INSERT INTO user_info (handle, updated_at) VALUES(?, ?)"
                    cursor.execute(sql, (res[0]['result']['handle'], res[0]['updated_at']))
                conn.commit()
                del res[0]['updated_at']
                ans.append(res[0])
            elif datetime_to_unix(result[0][3]) + 30 >= time.time():
                if not result[0][1]:
                    ans.append({
                        'sucess': 'true',
                        'result': {
                            'handle': result[0][0]
                        }
                    })
                else:
                    ans.append({
                        'sucess': 'true',
                        'result': {
                            'handle': result[0][0],
                            'rating': result[0][1],
                            'rank': result[0][2],
                        }
                    })
            else:
                res = grep_user(handle)
                if res[1] != 200:
                    ans.append(res[0])
                    continue
                if 'rating' in res[0]['result']:
                    sql = "UPDATE user_info SET handle = ?, rating = ?, rank = ?, updated_at = ? WHERE handle = ?"
                    cursor.execute(sql,
                                   (res[0]['result']['handle'], res[0]['result']['rating'], res[0]['result']['rank'],
                                    res[0]['updated_at'], handle))
                else:
                    sql = "UPDATE user_info SET handle = ?, updated_at = ? WHERE handle = ?"
                    cursor.execute(sql, (res[0]['result']['handle'], res[0]['updated_at'], handle))
                conn.commit()
                del res[0]['updated_at']
                ans.append(res[0])
        conn.close()
    except Exception as e:
        return {"message": "Internal Server Error"}, 501
    return ans, 200


def get_ratings_from_database(handle):
    try:
        conn = sqlite3.connect('cf.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_info WHERE handle = ?", (handle,))
        handles = []
        handles.append(handle)
        if len(cursor.fetchall()) == 0:
            t = get_userinfo_from_database(handles)
            if t[1] != 200:
                return t[0], t[1]
        conn.commit()
        conn.close()
    except Exception as e:
        return {"message": "Internal Server Error"}, 500
    try:
        conn = sqlite3.connect('cf.db')
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        # cursor.execute("SELECT * FROM user_info WHERE handle = ?", (handle,))
        # if len(cursor.fetchall() == 0):
        #     t = get_userinfo_from_database(handle)
        sql = "SELECT * FROM user_rating WHERE handle = ?"
        cursor.execute(sql, (handle,))
        result = cursor.fetchall()
        if len(result) == 0:
            res = grep_rating(handle)
            if res[1] != 200:
                return res[0], res[1]
            for contest in res[0]['result']:
                sql = "INSERT INTO user_rating(handle,contest_id,contest_name,rank,rating_updated_at,old_rating,new_rating,updated_at) VALUES(?,?,?,?,?,?,?,?) "
                temp = eval(str(contest))
                temp['ratingUpdatedAt'] = unix_to_datetime(convert_to_unix(temp['ratingUpdatedAt']))
                cursor.execute(sql, (
                    handle, temp['contestId'], temp['contestName'], temp['rank'], temp['ratingUpdatedAt'],
                    temp['oldRating'], temp['newRating'], res[0]['updated_at']))
                conn.commit()
            del res[0]['updated_at']
            conn.close()
            return res[0]['result'], res[1]
        elif datetime_to_unix(result[0][8]) + 30 >= time.time():
            ans = []
            for contest in result:
                ans.append({
                    "handle": contest[1],
                    "contestId": contest[2],
                    "contestName": contest[3],
                    "rank": contest[4],
                    "ratingUpdatedAt": unix_to_iso(datetime_to_unix(contest[7])),
                    "oldRating": contest[5],
                    'newRating': contest[6]
                })
            conn.close()
            return ans, 200
        else:
            res = grep_rating([handle])
            if res[1] != 200:
                return res[0], res[1]
            for contest in res[0]['result']:
                temp = eval(str(contest))
                contest_Id = temp['contestId']
                sql = "SELECT * FROM user_rating WHERE contest_id = ?"
                cursor.execute(sql, (contest_Id,))
                if len(cursor.fetchall()) == 0:
                    sql = "INSERT INTO user_rating(handle,contest_id,contest_name,rank,rating_updated_at,old_rating,new_rating,updated_at) VALUES(?,?,?,?,?,?,?,?) "
                    cursor.execute(sql, (
                        handle, temp['contestId'], temp['contestName'], temp['rank'], temp['ratingUpdatedAt'],
                        temp['oldRating'], temp['newRating'], res[0]['updated_at']))
                    conn.commit()
                else:
                    sql = "UPDATE user_rating SET updated_at = ? WHERE contest_id = ?"
                    cursor.execute(sql, (res[0]['updated_at'], contest_Id))
                    conn.commit()
            del res[0]['updated_at']
            conn.close()
            return res[0]['result'], res[1]
    except Exception as e:
        return {"message": "Internal Server Error"}, 503


@app.route('/batchGetUserInfo', methods=['get', 'post'])
def cin():
    handles = request.args.get("handles")
    handle_list = str(handles).split(',')

    ans = init_database()
    if ans[1] != 200:
        return ans[0], ans[1]

    ans = get_userinfo_from_database(handle_list)

    return jsonify(ans[0]), ans[1]


@app.route('/getUserRatings', methods=['get', 'post'])
def rating_query():
    handle = request.args.get("handle")
    ans = init_database()
    if ans[1] != 200:
        return ans[0], ans[1]
    ans = get_ratings_from_database(handle)

    return jsonify(ans[0]), ans[1]


@app.route('/', methods=['get', 'post'])
def grep_rating_html():
    return render_template('index.html')


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('127.0.0.1', 2333), app)
    server.serve_forever()


