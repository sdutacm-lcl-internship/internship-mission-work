import json
import requests
from flask import Flask
from flask import request
from flask import Response
from gevent import pywsgi

app = Flask(__name__)


def grep_user(user):

    url = 'https://codeforces.com/api/user.info'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 Edg/113.0.1774.42'
    }

    param = {
        "handles": user
    }

    try:#程序正常运行
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
            #请求响应异常
            ans = {
                "success": 'false',
                "type": '2',
                "message": "HTTP response with code" + str(resp_status_code),
                "details": {
                    "status": str(resp_status_code)
                }
            }
        else:#除去响应异常以及程序异常，剩下的为未收到合法响应
            ans = {
                "success": 'false',
                "type": '3',
                "message": "No valid HTTP response was received when querying this item"
            }
    except requests.exceptions.RequestException as e:#程序抛出异常
        ans = {
            "success": 'false',
            "type": '4',
            "message": "Internal Server Error"
        }
    return ans


@app.route('/', methods=['get', 'post'])
def cin():
    handles = request.args.get("handles")
    handle_list = str(handles).split(',')

    ans = []
    for user in handle_list:
        ans.append(grep_user(user))

    return Response(json.dumps(ans), mimetype='application/json')

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('127.0.0.1', 2333), app)
    server.serve_forever()
