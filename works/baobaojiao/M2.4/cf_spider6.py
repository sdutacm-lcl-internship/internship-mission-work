import json
import requests
import datetime
import time
import pytz
from flask import Flask, jsonify
from flask import request
from flask import Response
from gevent import pywsgi

app = Flask(__name__)

cache_userinfo = {}
cache_userrating = {}


def get_user_from_map(user):
    if user in cache_userinfo and cache_userinfo[user]["expiry_time"] > time.time():  # 若所查询用户在缓存内并且未超时，直接返回
        return cache_userinfo[user]["data"]

    data = grep_user(user)  # 走到这一步说明：用户不在缓存内，或者缓存内数据超时，重新获取

    if 'type' in data:  # 查询不到用户或请求异常时不加入缓存，‘type’存在于正常查询外的所有情况，所以可通过‘type’判断
        return data

    cache_userinfo[user] = {  # 将新数据存缓存
        "data": data,
        "expiry_time": time.time() + 15  # 15s限制
    }

    return cache_userinfo[user]['data']


def get_rating_from_map(handle):
    if handle in cache_userrating and cache_userrating[handle]['expiry_time'] > time.time():  # 判断缓存内是否存在合法数据
        print('map')
        return cache_userrating[handle]["data"], 200
    data = grep_rating(handle)

    if data[1] != 200:  # ’message‘存在于正常数据外的所有情况，用‘message’判断异常情况
        return data[0], data[1]

    cache_userrating[handle] = {  # 存入缓存
        "data": data[0],
        "expiry_time": time.time() + 15
    }
    print('server')
    return cache_userrating[handle]['data'], data[1]


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


def clear_cache_json(response):
    ans = {
        'message': 'invalid request'
    }
    status_code = 200
    try:
        for json_key in response.keys():
            if json_key != 'handles' and json_key != 'cacheType':
                status_code = 400
                return ans, status_code
        if (not 'cacheType' in response) or (
                response['cacheType'] != 'userInfo' and response['cacheType'] != 'userRatings'):
            status_code = 400
            return ans, status_code
        if response['cacheType'] == 'userInfo' and 'handles' in response:
            for handle in response['handles']:
                if handle in cache_userinfo:
                    del cache_userinfo[handle]

        elif response['cacheType'] == 'userInfo':
            cache_userinfo.clear()

        elif response['cacheType'] == 'userRatings' and 'handles' in response:
            for handle in response['handles']:
                if handle in cache_userrating:
                    del cache_userrating[handle]
        else:
            cache_userrating.clear()

        ans['message'] = 'ok'

    except requests.exceptions.RequestException as e:
        status_code = 400
        ans['message'] = 'invalid request'

    except Exception as e:
        status_code = 500
        ans['message'] = 'Internal Server Error'

    return ans, status_code

def clear_cache_webform(response):
    if 'handles' in response:
        list = response.getlist('handles')
        response = json.loads(json.dumps(response))
        response['handles'] = list
    elif 'handles[]' in response:
        list = response.getlisst('handles[]')
        response = json.loads(json.dumps(response))
        del response['handles[]']
        response['handles'] = list
    elif 'handles[0]' in response:
        cnt = 0
        resp = {}
        list = []
        for key, value in response.items():
            if key == 'handles[' + str(cnt) + ']':
                list.append(value)
                cnt += 1
            else:
                resp[key] = value
        if len(list) != 0:
            resp['handles'] = list
        response = json.loads(json.dumps(resp))

    else:
        response = json.loads(json.dumps(response))
    ans = clear_cache_json(response)
    return ans[0], ans[1]


@app.route('/clearCache', methods=['post'])
def clear_cache():
    if request.content_type == 'application/json':
        ans = clear_cache_json(request.json)
        return jsonify(ans[0]), ans[1]
    elif request.content_type == 'application/x-www-form-urlencoded':
        ans = clear_cache_webform(request.form)
        return jsonify(ans[0]), ans[1]


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
    ans = get_rating_from_map(handle)
    return jsonify(ans[0]), ans[1]


if __name__ == '__main__':
    server = pywsgi.WSGIServer(('127.0.0.1', 2333), app)
    server.serve_forever()
