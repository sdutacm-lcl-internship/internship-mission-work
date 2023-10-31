# coding=utf-8
import json
import socket
import requests
from gevent.pywsgi import WSGIServer
from fake_useragent import UserAgent
from flask import Flask, Response, request, render_template, jsonify

app = Flask(__name__)


def get_information(nickname):
    import subprocess
    try:
        e_url = f"https://codeforces.com/api/user.info"
        params = {"handles": nickname}
        response = requests.get(e_url, params=params)
        data = json.loads(response.text)

        if response.status_code == 200:
            if data["result"][0]["contribution"] == 0:
                # 无rank
                ans = {
                    "success": True,
                    "result": {
                        "handle": nickname
                    }
                }
                return ans
            else:
                # 正常
                ans = {
                    "success": True,
                    "result": {
                        "handle": nickname,
                        "rating": data["result"][0]["rating"],
                        "rank": data["result"][0]["rank"]
                    }
                }
                return ans
        elif response.status_code == 400:
            # 查无此人
            ans = {
                "success": False,
                "type": 1,
                "message": "no such handle"
            }
            return ans
        elif response.status_code == 401 or response.status_code == 402 or response.status_code == 403 or \
            response.status_code == 404 or response.status_code == 405 or response.status_code == 501 or \
            response.status_code == 502 or response.status_code == 503 or response.status_code == 504:
            # 响应错误
            ans = {
                "success": False,
                "type": 2,
                "message": "Http response with code" + str(response.status_code),
                "details": {
                    "status": response.status_code
                }
            }
            return ans
        elif response.status_code == 414:
            ans = {
                "success": False,
                "type": 3,
                "message": "Request timeout"
            }
            return ans
        else:
            # 无效响应
            ans = {
                "success": False,
                "type": 3,
                "message": "Request timeout"
            }
            return ans
    except:
        # 本身程序异常
        ans = {
            "success": False,
            "type": 4,
            "message": "Internal Server Error"
        }
        return ans



@app.route('/', methods=['GET'])
def solve():
    handles = request.args.get('handles')
    handles_list = handles.split(',')

    answer_message = []
    for it in handles_list:
        print(it)
        answer_message.append(get_information(it))
    return Response(json.dumps(answer_message), mimetype="application/json")


if __name__ == '__main__':
    WSGIServer(('127.0.0.1', 2333), app).serve_forever()







