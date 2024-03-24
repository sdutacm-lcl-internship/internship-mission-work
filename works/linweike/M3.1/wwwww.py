from flask import Flask,request,jsonify,Response, make_response
from datetime import timedelta, datetime
import time,os
import pytz
import requests
import json
import re
import sys

app = Flask(__name__)

map_user = {}
map_rating = {}

CACHE_TTL = 30  # 缓存过期时间，单位为秒

def get_ansjson(name):
    try:
        with open('data-user-info.json', 'r') as f:
            cache_data = json.load(f)
            expiry_time = datetime.fromisoformat(cache_data['expiry_time'])
            if expiry_time > datetime.now() and cache_data['name'] == name:
                return cache_data['data']
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass

    # 查询数据
    data = query_ansdata(name)

    # 将查询结果写入缓存文件
    expiry_time = datetime.now() + timedelta(seconds=CACHE_TTL)
    cache_data = {'expiry_time': expiry_time.isoformat(), 'data': data, 'name': name}
    with open('data-user-info.json', 'w') as f:
        json.dump(cache_data, f)

    return data

def get_resjson(name):
    try:
        with open('data-user-ratings.json', 'r') as f:
            cache_data = json.load(f)
            expiry_time = datetime.fromisoformat(cache_data['expiry_time'])
            if expiry_time > datetime.now() and cache_data['name'] == name:
                return cache_data['data']
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass

    # 查询数据
    data = get_resdata(name)

    # 将查询结果写入缓存文件
    expiry_time = datetime.now() + timedelta(seconds=CACHE_TTL)
    cache_data = {'expiry_time': expiry_time.isoformat(), 'data': data, 'name': name}
    with open('data-user-ratings.json', 'w') as f:
        json.dump(cache_data, f)

    return data

def query_ansdata(name):
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
        map_user[name] = {
            'data': data,
            'pop': datetime.now() + timedelta(seconds=15)
        }
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
    return data

def get_resdata(name):

    # if name in map_rating and map_rating[name]['pop'] > datetime.now():
    #     return map_rating[name]['data']

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

            # json_data = json.dumps(ans)
            # sys.stdout.write(json_data + '\n')
        # 情况2：未找到用户名
        elif status_code == 400:
            status_end_code = 404
            res = {
                'message': 'no such handle'
            }
        # 情况3：http响应错误
        else:
            status_end_code = status_code
            res = {
                'message': 'HTTP response with code {}'.format(status_code),
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
        }
    # 情况4： 未得到有效响应（无网络链接）
    except requests.exceptions.RequestException as e:
        status_end_code = 500
        return {
            'message': 'Request timeout'
        }
    #情况5：程序本身错误
    except :
        return {
            'success': False,
            'type': 4,
            'message': 'Internal Server Error'
        }
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
    return Response(json.dumps(results), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333, debug=True)


