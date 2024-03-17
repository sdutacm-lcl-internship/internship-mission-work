from flask import Flask,request,jsonify,Response
import requests
import json
import re
import sys
app = Flask(__name__)

def Get_ansjson(name):
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
                return {
                    'success': True,
                    'handle': user_data['handle'],
                    'rating': int(user_data['rating']),
                    'rank': user_data['rank']
                }
            elif 'handle' in user_data:
                return {
                    'success': True,
                    'handle': user_data['handle']
                }
            #json_data = json.dumps(ans)
            #sys.stdout.write(json_data + '\n')
        #情况2：未找到用户名
        elif status_code == 400:
            return {
                'success': False,
                'type': 1,
                'message': 'no such handle'
            }
        #情况3：http响应错误
        else:
            return {
                'success': False,
                'type': 2,
                'message': 'HTTP response with code {}'.format(status_code),
                'details': {
                    'status': status_code
                }
            }
    #情况4：未得到有效响应（连接错误）
    except requests.exceptions.ConnectionError as e:
        return {
            'success': False,
            'type': 3,
            'message': 'Request timeout',
        }
    #情况5：程序内部错误（无网络链接）
    except requests.exceptions.RequestException as e:
        return {
            'success': 'false',
            'type': 4,
            'message': 'Internal Server Error'
        }

@app.route('/')
def Get_handles():
    handles = request.args.get('handles').split(',')
    results = []
    for handle in handles:
        result = Get_ansjson(handle)
        results.append(result)
    return Response(json.dumps(results), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333, debug=True)
