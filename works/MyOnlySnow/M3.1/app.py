from flask import Flask, request, jsonify, Response, make_response
import requests
import json
from fake_useragent import UserAgent
from datetime import timedelta, datetime
import pytz

app = Flask(__name__)
app.config['DEBUG'] = True
file_Info = {}
file_Ratings = {}
valid_data = {}

def search_handles(handle):
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    ua = UserAgent().random
    headers = {'User-Agent': ua}
    global valid_data
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
            valid_data[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=30)
            }
            save_Info(list(valid_data.values()), 'data_info.js')
        else:
            data = {
                'success': True,
                'handle': handle,
                'rating': rating,
                'rank': rank
            }
            valid_data[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=30)
            }
            save_Info(list(valid_data.values()), 'data_info.js')
        return data

    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 400:
            data = {
                'success': False,
                'type': 1,
                'message': 'no such handle'
            }
            valid_data[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=30)
            }
            save_Info(list(valid_data.values()), 'data_info.js')
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
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
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
        valid_data[handle] = {
            'data': result,
            'out': datetime.now() + timedelta(seconds=30)
        }
        save_ratings(list(valid_data.values()), 'data_ratings.js')
        return result

    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 400:
            data = {
                'message': 'no such handle',
                'code': 404
            }
            valid_data[handle] = {
                'data': data,
                'out': datetime.now() + timedelta(seconds=30)
            }
            save_ratings(list(valid_data.values()), 'data_ratings.js')
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
    except Exception as ee :
        return {
            'message':str(ee) ,
            'code': 500
        }


def save_ratings(data, filename):
    existing_data = load_ratings(filename)
    for new_item in data:
        if "data" in new_item:
            new_data = new_item["data"]
            if isinstance(new_data, list):
                new_handles = [nd.get('handle') for nd in new_data]
            else:
                new_handles = [new_data.get('handle')]

            existing_data = [item for item in existing_data if "data" in item and
                             (isinstance(item["data"], list) and not any(
                                 d.get('handle') in new_handles for d in item["data"]) or
                              isinstance(item["data"], dict) and not item["data"].get('handle') in new_handles)]

    existing_data.extend(data)
    def json_serial(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

    with open(filename, 'w') as f:
        json.dump(existing_data, f, default=json_serial)


def load_ratings(filename):
    def json_deserial(obj):
        if 'out' in obj:
            obj['out'] = datetime.fromisoformat(obj['out'])
        return obj

    try:
        with open(filename, 'r') as f:
            data_list = json.load(f, object_hook=json_deserial)
            return data_list
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_Info(data, filename):
    existing_data = load_Info(filename)
    for new_data in data:
        handle = new_data.get('data', {}).get('handle', '')
        found = False
        for i, existing_item in enumerate(existing_data):
            if isinstance(existing_item, dict) and existing_item.get('data', {}).get('handle', '') == handle:
                existing_data[i] = new_data
                found = True
                break

        if not found:
            existing_data.append(new_data)
    def json_serial(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
    with open(filename, 'w') as f:
        json.dump(existing_data, f, default=json_serial)

def load_Info(filename):
    def json_deserial(obj):
        if 'out' in obj:
            obj['out'] = datetime.fromisoformat(obj['out'])
        if 'data' in obj:
            data_obj = obj['data']
            if 'out' in data_obj:
                data_obj['out'] = datetime.fromisoformat(data_obj['out'])
        return obj

    try:
        with open(filename, 'r') as f:
            data_list = json.load(f, object_hook=json_deserial)
            return data_list
    except (FileNotFoundError, json.JSONDecodeError):
        return []


@app.route('/batchGetUserInfo')
def URL_handles():
    file_Info = load_Info('data_info.js')
    handles = request.args.get('handles', '').split(',')
    results = []
    for handle in handles:
        now = datetime.now()
        valid_data = {data['data']['handle']: data for data in file_Info if 'handle' in data['data'] and data.get('out', now) > now}
        data = valid_data.get(handle, None)
        if data:
            results.append(data['data'])
        else:
            result = search_handles(handle)
            results.append(result)
    return Response(json.dumps(results), mimetype='application/json')


@app.route('/getUserRatings')
def URL_ratings():
    handle = request.args.get('handle', '')
    results = []
    file_Ratings = load_ratings('data_ratings.js')
    now = datetime.now()

    for rating in file_Ratings:
        if 'data' in rating:
            if isinstance(rating['data'], list):
                for r in rating['data']:
                    if 'handle' in r and r['handle'] == handle and rating['out'] > now:
                        rating['out'] = rating['out'].isoformat()
                        del rating['out']
                        response = make_response(json.dumps(rating['data']), 200)
                        response.headers['Content-Type'] = 'application/json'
                        return response
            elif isinstance(rating['data'], dict) and 'handle' in rating['data'] and rating['data'][
                'handle'] == handle and rating['out'] > now:
                del rating['out']
                rating['out'] = rating['out'].isoformat()
                response = make_response(json.dumps(rating['data']), 200)
                response.headers['Content-Type'] = 'application/json'
                return response
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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333, debug=True)