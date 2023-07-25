import copy
from flask import Flask, request, jsonify, Response
import requests
from datetime import datetime
import pytz
from flask import Flask, request, jsonify
from werkzeug.datastructures import MultiDict

app = Flask(__name__)

# 设置Application/X-WWW-Form-UrlEncoded请求体解析器
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
rating = {}
info = {}

@app.route('/clearCache', methods=['POST'])
def clear_cache():
    # 解析请求参数
    global info, rating
    if request.headers['Content-Type'].startswith('application/json'):
        data=request.get_json()
        type=data.get('cacheType',None)
        if "handles" not in data:
            handles=[]
        else:
            handles=data.get('handles')
            #判断获取的是不是字符串数组
            if isinstance(handles, list) and all(isinstance(item, str) for item in handles):
                handles=handles
            else:
                ans = {
                    'result': {
                        'message': 'invalid request'
                    },
                    'status': 400
                }
                return jsonify(ans["result"]), ans["status"]
    elif request.headers['Content-Type'].startswith('application/x-www-form-urlencoded'):
        data = request.form

        type = data.get('cacheType', None)
        if "handles" in data:
            handles = data.getlist("handles")
        else:
            handles = []
            i = 0
            while f'handles[{i}]' in data:
                handles.append(data[f'handles[{i}]'])
                i += 1
            if 'handles[]' in data:
                handles.extend(data.getlist('handles[]'))
    else:
        ans = {
            'result': {
                'message': 'invalid request'
            },
            'status': 400
        }
        return jsonify(ans["result"]), ans["status"]
    if type not in ['userInfo', 'userRatings']:
        ans = {
            'result': {
                'message': 'invalid request',
            },
            'status': 400
        }
        return jsonify(ans["result"]), ans["status"]


    if type == 'userInfo':
        total = copy.deepcopy(info)
    else:
        total = copy.deepcopy(rating)
    if handles == []:
        total = {}
    else:
        for handle in handles:
            if handle in total:#当请求体中handle存在的时候，才会pop掉，否则会key error
                # print(handle)
                total.pop(handle)
    #再把字典传递回去
    if type == 'userInfo':
        info = copy.deepcopy(total)
    else:
        rating = copy.deepcopy(total)
    # 返回成功响应
    return jsonify({'message': 'ok'}),200



def solve(username):
    url = "https://codeforces.com/api/user.info"
    # 请求的handles参数
    params = {
        "handles": username
    }

    try:
        # 1/0
        # 新建一个空的response对象，以便于异常的判断
        response = requests.Response()
        response = requests.get(url, params=params)
        number = response.status_code
        # print(number)
        data = response.json()
        # 没有收到响应的情况
        if response is None:
            user_info = {
                "success": False,
                "type": 3,
                "message": "No valid HTTP response was received when querying this item",
            }
            return user_info
        # 遇到异常http响应的情况,408是Request Timeout，504是Gateway Timeout
        elif number == 404 or number == 503 or number == 403 or number == 500 or number == 408 or number == 504:
            user_info = {
                "success": False,
                "type": 2,
                "message": data["comment"],
                "details": {
                    "status": number,
                }
            }
            return user_info
        # 前面写了没有响应的情况，这里再特判一下极小概率的情况
        elif "Content-Type" not in response.headers:
            user_info = {
                "success": False,
                "type": 3,
                "message": "No valid HTTP response was received when querying this item",
            }
            return user_info
        if data["status"] == "OK":
            for user in data["result"]:
                # 查看rank这个键是否存在，若不存在那么就是没用rating的用户
                if "rank" not in user:
                    user_info = {
                        "success": True,
                        "result": {
                            "handle": user['handle'],
                        }
                    }
                else:
                    user_info = {
                        "success": True,
                        "result": {
                            "handle": user["handle"],
                            "rating": user["rating"],
                            "rank": user["rank"]
                        }
                    }
                return user_info
        # 因为前面把错误的状态码都筛选掉了，所以剩下的就是查无此人的情况了
        elif data["status"] == "FAILED":
            user_info = {
                "success": False,
                "type": 1,
                "message": 'no such handle'
            }
            return user_info
    # 发现如果访问api失败也会收到状态码，这种情况下一般是503的状况
    # 访问失败，没有收到状态码就是断网的情况了
    except requests.exceptions.RequestException as e:
        if response is not None and response.status_code != 200 and response.status_code != 400:
            user_info = {
                "success": False,
                "type": 2,
                "message": "Abnormal response",
                "details": {
                    "status": response.status_code,
                }
            }
        # 断网了，没有收到响应
        else:
            user_info = {
                "success": False,
                "type": 3,
                "message": "No valid HTTP response was received when querying this item",
            }
        return user_info
    # 这是程序异常的情况
    except:
        user_info = {
            "success": False,
            "type": 4,
            "message": "Internal Server Error"
        }
        return user_info


@app.route('/batchGetUserInfo', methods=['GET'])
def query_handles():
    # 获取handles
    handles = request.args.get('handles')
    # 将handles按逗号分割成列表
    handle_list = handles.split(',')

    response_data = []
    for handle in handle_list:
        if isinfo(handle):
            response_data.append(info[handle]["result"])

        else:
            result = solve(handle)
            p = {
                "result": result,
                "time": datetime.now()
            }
            info[handle] = p
            response_data.append(result)

    # jsonify()函数简化了将数据转换为JSON响应的过程，并确保响应的Content-Type标头正确设置为application/json
    # 这样，浏览器或其他客户端会正确地解析返回的JSON数据了
    return jsonify(response_data)


# 记录查询函数体
def find(username):
    url = 'https://codeforces.com/api/user.rating'
    params = {
        'handle': username,
    }
    try:
        response = requests.get(url=url, params=params)
        number = response.status_code
        if number == 200:
            data = response.json()
            for one in data["result"]:
                dt = datetime.fromtimestamp(one["ratingUpdateTimeSeconds"], pytz.timezone('Asia/Shanghai'))
                dtstring = dt.isoformat()

                one["ratingUpdatedAt"] = dtstring
                one.pop("ratingUpdateTimeSeconds")  # 把原来的时间戳键值删掉
            data["status"] = 200
            return data
        elif number == 400:
            data = {
                'status': 404,
                "result": {
                    "message": 'no such handle',
                }
            }
            return data
        else:
            data = {
                'status': number,
                "result": {
                    "message": 'Abnormal response',
                }
            }
            return data
    except requests.exceptions.RequestException as e:
        data = {
            'status': 503,
            "result": {
                "message": 'Connection interruption',
            }
        }
        return data
    except:
        data = {
            'status': 500,
            "result": {
                "message": 'program exception',
            }
        }
        return data


# 单用户查询用户记录
@app.route('/getUserRatings', methods=['GET'])
def getUserRatings():
    handle = request.args.get('handle')
    if israting(handle):

        find_list = rating[handle]
    else:
        find_list = find(handle)
        p = {
            "time": datetime.now(),
            "result": find_list["result"],
            "status": find_list["status"]
        }
        rating[handle] = p
        # print(rating[handle])
    # jsonify函数返回的是一个response对象，所以可以在后面直接加状态码
    return jsonify(find_list["result"]), find_list["status"]


def israting(username):
    if username in rating:
        nowtime = datetime.now()
        lefttime = rating[username]['time']
        t = (nowtime - lefttime).total_seconds()
        if t < 15:
            return True
        else:
            rating.pop(username)
            return False
    else:
        return False


def isinfo(username):
    if username in info:
        nowtime = datetime.now()
        lefttime = info[username]['time']
        t = (nowtime - lefttime).total_seconds()
        if t < 15:
            return True
        else:
            info.pop(username)
            return False
    else:
        return False


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333)
