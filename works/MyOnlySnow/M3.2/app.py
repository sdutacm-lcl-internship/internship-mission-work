import flask
from flask import Flask, request, jsonify, Response, make_response,template_rendered,render_template
import requests
import json
from fake_useragent import UserAgent
from datetime import timedelta, datetime
import sqlite3
import pytz

app = Flask(__name__,template_folder='templates', static_folder='static')
app.config['DEBUG'] = True

def update_user_info(handle,rating,rank):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        now = datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()
        cursor.execute('''
        INSERT OR REPLACE INTO user_info(handle,rating,rank,updatedTime)
        VALUES(?,?,?,?)
        ''',(handle,rating,rank,now)
        )
        conn.commit()

def update_user_rating(handle,contest_id,contest_name,rank,old_rating,new_rating,ratingUpdatedAt):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        now = datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()
        cursor.execute("SELECT handle FROM user_info WHERE handle = ?", (handle,))
        data = cursor.fetchone()
        if data is None:
            search_handles(handle)
        cursor.execute(
            '''
                    INSERT OR REPLACE INTO user_ratings(handle,contest_id,contest_name,rank,old_rating,new_rating,ratingUpdatedAt,updatedTime)
                    VALUES(?,?,?,?,?,?,?,?)
            ''',(handle,contest_id,contest_name,rank,old_rating,new_rating,ratingUpdatedAt,now)
        )
        conn.commit()

def search_handles(handle):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT rating,rank FROM user_info
        WHERE handle = ? AND updatedTime > ?
        ''',(handle,(datetime.now(pytz.timezone('Asia/Shanghai'))-timedelta(seconds=30)).isoformat()))
        row = cursor.fetchone()
        if row:
            data =[]
            result = {}
            rating, rank = row
            if rating and rank:
                result = {
                    'handle': handle,
                    'rating': rating,
                    'rank': rank
                }
                data = {
                    'success':True,
                    'result':result
                    }
            else:
                result = {
                    'handle': handle
                }
                data = {
                    'success': True,
                    'result': result
                }
            return data


    url = f"https://codeforces.com/api/user.info?handles={handle}"
    ua = UserAgent().random
    headers = {'User-Agent': ua}
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        Json = response.json()
        info_list = Json.get('result', [])
        info = info_list[0]
        handle = info.get('handle', '')
        rating = info.get('rating', 0)
        rank = info.get('rank', '')
        max = info.get('maxRating', '')
        update_user_info(handle,rating,rank)
        conn.close()
        if not rating or max == []:
            result = {
                'handle': handle
            }
            data = {
                'success': True,
                'result': result
            }
        else:
            result = {
                'handle': handle,
                'rating': rating,
                'rank': rank
            }
            data = {
                'success': True,
                'result': result
            }
        return data

    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 400:
            data = {
                'success': False,
                'type': 1,
                'message': 'no such handle'
            }
            return data
        else:
            data = {
                'success': False,
                'type': 2,
                'message': f'HTTP response with code {error.response.status_code}',
                'details': {
                    'status': error.response.status_code
                }
            }
    except requests.exceptions.ConnectionError:
        data = {
            'success': False,
            'type': 3,
            'message': "Nice! Request Failed due to Network issues."
        }
    except Exception:
        data = {
            'success': False,
            'type': 4,
            'message': "Internal Server Error"
        }
    return data


def search_ratings(handle):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
        SELECT contest_id,contest_name,rank,old_rating,new_rating,ratingUpdatedAt FROM user_ratings
        WHERE handle = ? AND updatedTime > ?
        ''',(handle,(datetime.now(pytz.timezone('Asia/Shanghai'))-timedelta(seconds=30)).isoformat()))
        rows = cursor.fetchall()
        if rows:
            data = []
            for row in rows:
                contest_id, contest_name, rank, old_rating, new_rating, ratingUpdatedAt = row
                data.append({
                    'handle': handle,
                    'contest_id': contest_id,
                    'contest_name': contest_name,
                    'rank': rank,
                    'ratingUpdatedAt': ratingUpdatedAt,
                    'old_rating': old_rating,
                    'new_rating': new_rating
                })
            return data


    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    ua = UserAgent().random
    headers = {'User-Agent': ua}
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        Json = response.json()
        info_list = Json.get('result', [])
        result = []
        for info in info_list:
            contestId = info.get('contestId', 0)
            contestName = info.get('contestName', '')
            rank = info.get('rank', 0)
            ratingUpdateTimeSeconds = info.get('ratingUpdateTimeSeconds', 0)
            oldRating = info.get('oldRating', 0)
            newRating = info.get('newRating', 0)
            time = datetime.fromtimestamp(ratingUpdateTimeSeconds, pytz.timezone('Asia/Shanghai'))
            ratingUpdatedAt = time.isoformat()
            if contestId:
                update_user_rating(handle,contestId,contestName,rank,oldRating,newRating,ratingUpdatedAt)
            result.append(
                {
                    'handle': handle,
                    'contestId': contestId,
                    'contestName': contestName,
                    'rank': rank,
                    'ratingUpdatedAt': ratingUpdatedAt,
                    'oldRating': oldRating,
                    'newRating': newRating
                }
            )
        conn.close()
        if result == []:
            result = {
                'handle': handle,
                'message': 'This handle does not have a competition record'
            }
        return result


    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 400:
            data = {
                'message': 'no such handle',
                'code': 404
            }
            return data
        else:
            return {
                'message': f'HTTP response with code {error.response.status_code}',
                'code': error.response.status_code
            }
    except requests.exceptions.ConnectionError:
        return {
            'message': "Nice! Request Failed due to Network issues.",
            'code': 503
        }
    except Exception as error:
        print(error)
        return {
            'message': "Internal Server Error",
            'code':500
        }


@app.route('/batchGetUserInfo')
def URL_handles():
    handles = request.args.get('handles', '').split(',')
    results = []
    for handle in handles:
        result = search_handles(handle)
        results.append(result)
    # 会换行但是按照字典序
    # response = jsonify(results)
    # response.headers['Content-Type'] = 'application/json'
    # return response,200
    # 不换行但是顺序正确
    return Response(json.dumps(results), mimetype='application/json')


@app.route('/getUserRatings')
def URL_ratings():
    handle = request.args.get('handle', '')
    results = []
    results = search_ratings(handle)
    if 'message' in results and 'code' in results:
        result = {
            'message': results['message']
        }
        response = make_response(json.dumps(result), results['code'])
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(results), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/')
def HTML():
    return flask.render_template('dog.html')

def creat_file():
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_info (
                 handle VARCHAR PRIMARY KEY NOT NULL,
                rating INT,
                rank VARCHAR,
                updatedTime DATETIME NOT NULL
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
                        ratingUpdatedAt DATETIME NOT NULL,
                        updatedTime DATETIME NOT NULL,
                        FOREIGN KEY (handle) REFERENCES user_info (handle),
                        UNIQUE(handle, contest_id) ON CONFLICT REPLACE
                    );
                ''')
    conn.commit()

if __name__ == '__main__':
    creat_file()
    app.run(host='127.0.0.1', port=2333, debug=True)
