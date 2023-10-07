import json
import time
import pytz
import requests
import datetime
from flask_caching import Cache
from fake_useragent import UserAgent
from flask import Flask, request, Response
from gevent import os

app = Flask(__name__)


# 爬虫获得 对应的数据 Info
def get_information(nickname):
    try:
        e_url = f"https://codeforces.com/api/user.info"
        params = {
            "handles": nickname
        }
        response = requests.get(e_url, params=params)
        data = json.loads(response.text)

        print(response.status_code)
        print(nickname)

        if response.status_code == 200:
            # 查无此人
            if data["status"] == "FAILED":
                ans = {
                    "success": "False",
                    "type": 1,
                    "message": "no such handle"
                }
                return ans
            # 无rank
            elif data["result"][0]["contribution"] == 0:
                ans = {
                    "success": "False",
                    "result": {
                        "handle": nickname
                    }
                }
                return ans
            # 一切正常
            else:
                ans = {
                    "success": "True",
                    "result": {
                        "handle": data["result"][0]["handle"],
                        "rating": data["result"][0]["rating"],
                        "rank": data["result"][0]["rank"]
                    }
                }
                return ans
        # 响应错误
        elif response.status_code == 401 or response.status_code == 402 or response.status_code == 403 or \
            response.status_code == 404 or response.status_code == 405 or response.status_code == 501 or \
            response.status_code == 502 or response.status_code == 503 or response.status_code == 504 or \
            response.status_code == 400:
            ans = {
                "success": "False",
                "type": 2,
                "message": "Http response with code" + str(response.status_code),
                "details": {
                    "status": response.status_code
                }
            }
            return ans
        # 无效响应
        else:
            ans = {
                "success": "False",
                "type": 3,
                "message": "No legitimate response was received"
            }
            return ans
    except:
        # 本身程序异常
        ans = {
            "success": "False",
            "type": 4,
            "message": "Program error"
        }
        return ans


#获取 info 的信息 开始判断
@app.route('/batchGetUserInfo', methods=['GET'])
def solve():
    handles = request.args.get('handles')
    handle_list = handles.split(',')

    answer_message = []
    for handle in handle_list:
        # 判断文件是否为空
        if os.path.isfile('data-user-info.json') and os.path.getsize('data-user-info.json') > 0:
            # 文件存在开始读出
            with open('data-user-info.json', 'r', encoding='utf8') as fp:
                try:
                    data = json.load(fp)
                except json.decoder.JSONDecodeError as e:
                    print(f"Failed to parse JSON: {e}")
        else:
            # 文件不存在或为空，创建新的数据结构
            data = {}

        # 时间合适
        if handle in data and time.time() - data[handle]['timestamp'] <= 30:
            temp = data[handle]['data']
            answer_message.append(temp)
        # 时间不合适或者没有更新
        else:
            temp = get_information(handle)
            answer_message.append(temp)
            if temp['success'] != False:
                data[handle] = {
                    'data': temp,
                    'timestamp': time.time()
                }
                # 将数据写回 JSON 文件
                with open('data-user-info.json', 'w', encoding='utf8') as fp:
                    json.dump(data, fp)

    return Response(json.dumps(answer_message), mimetype="application/json")

# 爬虫获得 对应的数据 Info
def get_UserRating_two(nickname):
    try:
        e_url = f"https://codeforces.com/api/user.rating?handle={nickname}"
        headers = {'User-Agent': UserAgent().random}
        response = requests.get(url=e_url, headers=headers)

        data = json.loads(response.text)
        print(data)
        print(nickname)

        ans = []
        if response.status_code == 200:

            for every_thing in data['result']:
                dt = datetime.datetime.fromtimestamp(every_thing['ratingUpdateTimeSeconds'],
                                                     pytz.timezone('Asia/Shanghai'))
                dtt = dt.isoformat()

                gett = {
                    "handle": every_thing['handle'],
                    "contestId": every_thing["contestId"],
                    "contestName": every_thing['contestName'],
                    "rank": every_thing['rank'],
                    "ratingUpdatedAt": dtt,
                    "oldRating": every_thing['oldRating'],
                    "newRating": every_thing['newRating'],
                }
                ans.append(gett)
            return ans
        elif response.status_code == 400:
            # 查无此人
            ans = {"message": "no such handle"}
            return ans
        elif response.status_code == 401 or response.status_code == 402 or response.status_code == 403 or \
            response.status_code == 405 or response.status_code == 501 or response.status_code == 502 or \
            response.status_code == 503 or response.status_code == 504:
            # 响应错误
            ans = {"message": "Http response with code" + str(response.status_code)}
            return ans
        else:
            # 无效响应
            ans = {"message": "No legitimate response was received"}
            return ans
    except:
        # 本身程序异常
        ans = {"message": "Program error"}
        return ans


# 获取 rating 的信息 开始判断
@app.route('/getUserRatings', methods=['GET'])
def getUserRatings():
    handle = request.args.get('handle')

    answer_message = []
    if os.path.isfile('data-user-ratings.json') and os.path.getsize('data-user-ratings.json') > 0:
        with open('data-user-ratings.json', 'r', encoding='utf8') as fp:
            try:
                data = json.load(fp)
            except json.decoder.JSONDecodeError as e:
                print(f"Failed to parse JSON: {e}")
    else:
        # 文件不存在或为空，创建新的数据结构
        data = {}

    if handle in data and time.time() - data[handle]['timestamp'] <= 30:
        temp = get_UserRating_two(handle)
        answer_message.append(temp)
    else:
        temp = get_UserRating_two(handle)
        answer_message.append(temp)
        data[handle] = {
            'data': temp,
            'timestamp': time.time()
        }
        # 将合并后的数据写回 JSON 文件
        with open('data-user-ratings.json', 'w', encoding='utf8') as fp:
            json.dump(data, fp)
    return Response(json.dumps(answer_message), mimetype="application/json")



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333, debug=True)




