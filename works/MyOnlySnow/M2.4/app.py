from flask import Flask, request, jsonify, Response, make_response
import urllib.error
import requests
import json
from fake_useragent import UserAgent
from datetime import timedelta, datetime
import sqlite3
import time
import pytz
from urllib.parse import parse_qs

app = Flask(__name__)
app.config['DEBUG'] = True
cache = {}


def search_handles(handle):
    if handle in cache and cache[handle]['out'] > datetime.now():
        return cache[handle]['data']

    file_data = load_file('data_info.js')
    now = datetime.now()
    valid_data = {key: value for key, value in file_data.items() if value.get('out', now) > now}
    data = valid_data.get(handle, None)

    if data:
        cache[handle] = {
            'data': data['data'],
            'out': data['out']
        }
        return data['data']

    url = f"https://codeforces.es/api/user.info?handles={handle}"
    ua = UserAgent().random
    headers = {'User-Agent': ua}
    try:
        response = requests.get(url=url,headers=headers)
        response.raise_for_status()
        Json = response.json()
        info_list = Json.get('result', [])
        info = info_list[0]
        handle = info.get('handle', '')
        rating = info.get('rating', 0)
        rank = info.get('rank', '')
        max = info.get('maxRating', '')
        if not rating or max == []:
            data = {
                'success': True,
                'handle': handle
            }
            cache[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=15)
            }
            file_data[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=30)
            }
            save_file(file_data, 'data_info.js')
        else:
            data = {
                'success': True,
                'handle': handle,
                'rating': rating,
                'rank': rank
            }
            cache[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=15)
            }
            file_data[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=30)
            }
            save_file(file_data, 'data_info.js')
        return data

    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 400:
            data = {
                'success': False,
                'type': 1,
                'message': 'no such handle'
            }
            cache[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=15)
            }
            file_data[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=30)
            }
            save_file(file_data, 'data_info.js')
        else:
            data = {
                'success': False,
                'type': 2,
                'message': f'HTTP response with code {error.response.status_code}',
                'details': {
                    'status': error.response.status_code
                }
            }
    except urllib.error.URLError as error:
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
    if handle in cache and cache[handle]['out'] > datetime.now():
        return cache[handle]['data']

    file_data = load_file('data_ratings.js')
    now = datetime.now()
    valid_data = {key: value for key, value in file_data.items() if value.get('out', now) > now}
    data = valid_data.get(handle,None)

    if data:
        cache[handle] = {
            'data': data['data'],
            'out': data['out']
        }
        return data['data']

    url = f"https://codeforces.es/api/user.rating?handle={handle}"
    ua = UserAgent().random
    headers = {'User-Agent': ua}
    try:
        response = requests.get(url=url,headers=headers)
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
        if result == []:
            result = {
                'handle': handle,
                'message': 'This handle does not have a competition record'
            }
        cache[handle] = {
            'data': result,
            'out': datetime.now() + timedelta(seconds=15)
        }
        file_data[handle] = {
            'data': result,
            'out': datetime.now() + timedelta(seconds=30)
        }
        save_file(file_data, 'data_ratings.js')
        return result


    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 400:
            data = {
                'message': 'no such handle',
                'code': 404
            }
            cache[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=15)
            }
            file_data[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=30)
            }
            save_file(file_data, 'data_ratings.js')
            return data
        else:
            return {
                'message': f'HTTP response with code {error.response.status_code}',
                'code' : error.response.status_code
            }
    except requests.exceptions.ConnectionError:
        return {
            'message': "Nice! Request Failed due to Network issues.",
            'code': 503
        }
    except Exception:
        return {
            'message': "Internal Server Error",
            'code': 500
        }


def save_file(data, filename):
    def json_serial(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

    existing_data = load_file(filename)
    for key, value in data.items():
        existing_data[key] = value

    with open(filename, 'w') as f:
        json.dump(existing_data, f, default=json_serial)

def load_file(filename):
    def json_deserial(obj):
        if 'out' in obj:
            obj['out'] = datetime.fromisoformat(obj['out'])
        return obj

    try:
        with open(filename, 'r') as f:
            return json.load(f, object_hook=json_deserial)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

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
                'message':results['message']
        }
        return jsonify(result), results['code']
    else:
        return json.dumps(results)


@app.route('/clearCache', methods=['POST'])
def clear_cache():
    try:
        if request.content_type == 'application/json':
            data = request.get_json()
            handles = data.get('handles', [])
            if isinstance(handles, str):
                return jsonify({'message': 'Invalid request'}), 400
            for h in handles:
                if not isinstance(h, str) or len(h) <= 1:
                    return jsonify({'message': 'Invalid request'}), 400

        elif request.content_type == 'application/x-www-form-urlencoded':
            data = {}
            for key, values in request.form.lists():
                if key == 'cacheType':
                    data[key] = values[0]
                elif key.startswith('handles'):
                    field_name = key.split('[')[0]
                    if field_name not in data:
                        data[field_name] = []
                    for value in values:
                        if not isinstance(value, str) or len(value) <= 1:
                            return jsonify({'message': 'invalid request'}), 400
                        elif value == 'TRUE' or value == 'FALSE' or value == 'false' or value == 'true' or value == 'True' or value == 'False':
                            return jsonify({'message': 'invalid request'}), 400
                        data[field_name].append(value)
        else:
            return jsonify({'message': 'invalid request'}), 400

        cache_type = data.get('cacheType')
        print(cache_type)
        handles = data.get('handles', [])
        print(handles)

        if cache_type not in ('userInfo', 'userRatings'):
            return jsonify({'message': 'invalid request'}),400
        if not handles:
            cache.pop(cache_type, None)
        else:
            for handle in handles:
                print(handle)
                cache_entry = cache.get(handle, {}).get(cache_type)
                if cache_entry:
                    del cache[handle][cache_type]
                print(cache)
        return jsonify({'message': 'ok'}), 200

    except Exception:
        return jsonify({'message': 'invalid request'}), 400

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333, debug=True)
