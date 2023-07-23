from flask import Flask, request, jsonify, Response, make_response
import requests
import json
from fake_useragent import UserAgent
from datetime import timedelta, datetime
import sqlite3
import time
import pytz


app = Flask(__name__)
app.config['DEBUG'] = True


def search_handles(handle):
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
        else:
            data = {
                'success': True,
                'handle': handle,
                'rating': rating,
                'rank': rank
            }
        return data

    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 400:
            data = {
                'success': False,
                'type': 1,
                'message': 'no such handle'
            }
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
                'message':results['message']
        }
        return jsonify(result), results['code']
    else:
        return json.dumps(results)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333, debug=True)
