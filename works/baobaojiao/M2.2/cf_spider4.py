import json
import requests
import datetime
from flask import Flask, jsonify
from flask import request
from flask import Response
from gevent import pywsgi
import pytz

app = Flask(__name__)


def unix_to_iso(unix_time):
    Date_Time = datetime.datetime.fromtimestamp(unix_time, pytz.timezone('Asia/Shanghai'))
    Iso_Time = Date_Time.isoformat()
    return Iso_Time


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
                    "success": "true",
                    "result": {
                        "handle": user,
                        "rating": page['result'][0]['rating'],
                        "rank": page['result'][0]['rank']
                    }
                }
            else:
                ans = {
                    "success": "true",
                    "result": {
                        "handle": user
                    }
                }
        elif page['status'] == "FAILED":
            ans = {
                "success": "false",
                "type": 1,
                "message": "no such handle"
            }
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
        else:  # 除去响应异常以及程序异常，剩下的为未收到合法响应
            ans = {
                "success": 'false',
                "type": '3',
                "message": "No valid HTTP response was received when querying this item"
            }
    except requests.exceptions.RequestException as e:  # 程序抛出异常
        ans = {
            "success": 'false',
            "type": '4',
            "message": "Internal Server Error"
        }
    except Exception as e:
        ans = {
            "success": 'false',
            "type": "4",
            "message": "Internal Server Error"
        }
    return ans


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

        ans = []
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
                ans.append(temp)
        elif resp_status == 400:
            ans = {
                'status': '404',
                "message": "no such handle"
            }
        elif resp_status == 401 or resp_status == 403 or resp_status == 404 or resp_status == 500 or resp_status == 502 or resp_status == 503 or resp_status == 504:
            ans = {
                'status': resp_status,
                "message": "HTTP response with code" + str(resp_status)
            }
    except requests.exceptions.RequestException as e:  # 程序抛出异常
        ans = {
            'status': '500',
            "message": "Internal Server Error"
        }
    except Exception as e:
        ans = {
            'status': '500',
            "message": "Internal Server Error"
        }
    return ans


@app.route('/batchGetUserInfo', methods=['get', 'post'])
def cin():
    handles = request.args.get("handles")
    handle_list = str(handles).split(',')

    ans = []
    for user in handle_list:
        ans.append(grep_user(user))

    return Response(json.dumps(ans), mimetype='application/json')


@app.route('/getUserRatings', methods=['get', 'post'])
def rating_query():
    handle = request.args.get("handle")
    ans = grep_rating(handle)
    return jsonify(ans), 200 if not 'status' in ans else ans['status']


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('127.0.0.1', 2333), app)
    server.serve_forever()
