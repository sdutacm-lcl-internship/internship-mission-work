from flask import Flask, request, jsonify, Response
import urllib.error
import urllib.request
import json
from fake_useragent import UserAgent
import datetime
import redis
import time
import pytz

app = Flask(__name__)
app.config['DEBUG'] = True

def search_handles(handle):
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    ua = UserAgent().random
    headers = {'User-Agent': ua}
    request = urllib.request.Request(url=url, headers=headers)
    try:
        response = urllib.request.urlopen(request)
        content = response.read().decode("utf-8")
        Json = json.loads(content)
        info_list = Json.get('result', [])
        info = info_list[0]
        handle = info.get('handle', '')
        rating = info.get('rating', 0)
        rank = info.get('rank', '')
        max = info.get('maxRating', '')
        if not rating or max == []:
            return {
                'success': True,
                'handle': handle
            }
        else:
            return {
                'success': True,
                'handle': handle,
                'rating': rating,
                'rank': rank
            }
    except urllib.error.HTTPError as error:
        if error.code == 400:
            return {
                'success': False,
                'type': 1,
                'message': 'no such handle'
            }
        else:
            return {
                'success': False,
                'type': 2,
                'message': f'HTTP response with code {error.code}',
                'details': {
                    'status': error.code
                }
            }
    except urllib.error.URLError as error:
        return {
            'success': False,
            'type': 3,
            'message': "Nice! Request Failed due to Network issues."
        }
    except Exception as e:
        return {
            'success': False,
            'type': 4,
            'message': "Internal Server Error"
        }

def search_ratings(handle):
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    ua = UserAgent().random
    headers = {'User-Agent': ua}
    request = urllib.request.Request(url=url, headers=headers)
    try:
        response = urllib.request.urlopen(request)
        content = response.read().decode("utf-8")
        Json = json.loads(content)
        info_list = Json.get('result', [])
        result = []
        for info in info_list:
            contestId = info.get('contestId', 0)
            contestName = info.get('contestName', '')
            rank = info.get('rank', 0)
            ratingUpdateTimeSeconds = info.get('ratingUpdateTimeSeconds', 0)
            oldRating = info.get('oldRating', 0)
            newRating = info.get('newRating', 0)
            time = datetime.datetime.fromtimestamp(ratingUpdateTimeSeconds,pytz.timezone('Asia/Shanghai'))
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

        return result

    except urllib.error.HTTPError as error:
        if error.code == 400:
            return {
                'message': 'no such handle'
            }
        else:
            return {
                'message': f'HTTP response with code {error.code}'
            }
    except urllib.error.URLError as error:
            return {
                'message': "Nice! Request Failed due to Network issues."
            }
    except Exception as e:
        return {
            'message': "Internal Server Error"
        }

@app.route('/batchGetUserInfo')
def URL_handles():  # put application's code here
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
    return json.dumps(results)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333, debug=True)
