import json
import requests
import datetime
import time
import pytz
from flask import Flask
from flask import request
from flask import Response
from gevent import pywsgi

app = Flask(__name__)

cache_userinfo = {}
cache_userrating = {}


def get_user_from_map(user):
    if user in cache_userinfo and cache_userinfo[user]["expiry_time"] > time.time():  # 若所查询用户在缓存内并且未超时，直接返回
        print("通过map获取user")
        return cache_userinfo[user]["data"]

    data = grep_user(user)  # 走到这一步说明：用户不在缓存内，或者缓存内数据超时，重新获取

    if 'type' in data:  # 查询不到用户或请求异常时不加入缓存，‘type’存在于正常查询外的所有情况，所以可通过‘type’判断
        return data

    cache_userinfo[user] = {  # 将新数据存缓存
        "data": data,
        "expiry_time": time.time() + 15  # 15s限制
    }
    print("通过server获取user")
    return cache_userinfo[user]['data']


def get_rating_from_map(handle):
    if handle in cache_userrating and cache_userrating[handle]['expiry_time'] > time.time():  # 判断缓存内是否存在合法数据
        return cache_userrating[handle]["data"]

    data = grep_rating(handle)

    if 'message' in data[0]:  # ’message‘存在于正常数据外的所有情况，用‘message’判断异常情况
        return data

    cache_userrating[handle] = {  # 存入缓存
        "data": data,
        "expiry_time": time.time() + 15
    }

    return cache_userrating[handle]['data']


def unix_to_iso(unix_time):
    Date_Time = datetime.datetime.fromtimestamp(unix_time, pytz.timezone('Asia/Shanghai'))  # 转换Unix时间戳
    Iso_Time = Date_Time.isoformat()  # 转换为iso
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
    return ans


def grep_rating(handle):
    url = 'https://codeforces.com/api/user.rating'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 Edg/113.0.1774.42'
    }

    param = {
        "handle": handle
    }

    response = requests.get(url=url, headers=headers, params=param)
    page = response.json()
    resp_status = response.status_code

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
        ans.append({"message": "no such handle"})
    else:
        ans.append({"message": "HTTP response with code " + str(resp_status)})
    return ans


@app.route('/batchGetUserInfo', methods=['get', 'post'])
def cin():
    handles = request.args.get("handles")
    handle_list = str(handles).split(',')

    ans = []
    for user in handle_list:
        ans.append(get_user_from_map(user))

    return Response(json.dumps(ans), mimetype='application/json')


@app.route('/getUserRatings', methods=['get', 'post'])
def rating_query():
    handle = request.args.get("handle")
    return Response(json.dumps(get_rating_from_map(handle)), mimetype='application/json')


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('127.0.0.1', 2333), app)
    server.serve_forever()
