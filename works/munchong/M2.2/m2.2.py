import datetime
import json

import pytz
import requests
from fake_useragent import UserAgent
from flask import Flask, request, Response
from gevent.pywsgi import WSGIServer


app = Flask(__name__)

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
            if data["status"] == "FAILED":
                # 查无此人
                ans = {
                    "success": "False",
                    "type": 1,
                    "message": "no such handle"
                }
                return ans
            elif data["result"][0]["contribution"] == 0:
                # 无rank
                ans = {
                    "success": "False",
                    "result": {
                        "handle": nickname
                    }
                }
                return ans
            else:
                # 正常
                ans = {
                    "success": "True",
                    "result": {
                        "handle": data["result"][0]["handle"],
                        "rating": data["result"][0]["rating"],
                        "rank": data["result"][0]["rank"]
                    }
                }
                return ans
        elif response.status_code == 401 or response.status_code == 402 or response.status_code == 403 or \
            response.status_code == 404 or response.status_code == 405 or response.status_code == 501 or \
            response.status_code == 502 or response.status_code == 503 or response.status_code == 504 or \
            response.status_code == 400:
            # 响应错误
            ans = {
                "success": "False",
                "type": 2,
                "message": "Http response with code" + str(response.status_code),
                "details": {
                    "status": response.status_code
                }
            }
            return ans
        else:
            # 无效响应
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



@app.route('/batchGetUserInfo', methods=['GET'])
def solve():
    handles = request.args.get('handles')
    handle_list = handles.split(',')

    answer_message = []
    for it in handle_list:
        answer_message.append(get_information(it))
    return Response(json.dumps(answer_message), mimetype="application/json")


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
                dt = datetime.datetime.fromtimestamp(every_thing['ratingUpdateTimeSeconds'], pytz.timezone('Asia/Shanghai'))
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
            # 无rank
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


@app.route('/getUserRatings', methods=['GET'])
def getUserRatings():
    handle = request.args.get('handle')
    answer_message = get_UserRating_two(handle)
    return Response(json.dumps(answer_message), mimetype="application/json")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333, debug=True)