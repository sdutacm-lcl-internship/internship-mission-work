from flask import Flask,request,jsonify,Response
from fake_useragent import UserAgent
import requests
import json
url="https://codeforces.com/api/user.info"
headers={
    'user-Agent':UserAgent().random
}
def solve(name):
    params = {
        "handles": name
    }
    try:
        response=requests.get(url=url,params=params,headers=headers)
        status_code =response.status_code
        if status_code==200:        # 此项 handle 可以查询到
            Json=json.loads(response.text)
            user=Json['result'][0]
            if 'rating' in user:
                return {
                    'success':True,
                    'result':{
                        'handle':user['handle'],
                        'rating':int(user['rating']),
                        'rank':user['rank']
                    }
                }
            else:
                return {
                    'success':True,
                    'result':{
                        'handle':user['handle']
                    }
                }
        elif status_code==400:      # 此项 handle 无法找到
            return {
                'success':False,
                'type':1,
                'message':'no such handle'
            }
        else:                       # 在查询此项时遭遇异常 HTTP 响应
            return {
                'success':False,
                'type':2,
                'message':'HTTP response with code {}'.format(status_code)
            }
    except requests.exceptions.ConnectionError or requests.exceptions.RequestException as e:    # 在查询此项时未收到有效 HTTP 响应
        return {
            'success':False,
            'type':3,
            'message':'Request timeout'
        }
    except :                        # 在查询此项时程序发生运行时异常
        return {
            'success':False,
            'type':4,
            'message':'Internal Server Error'
        }


app=Flask(__name__) # 定义一个Flask的实例

@app.route('/') # 装饰器，将 URL 路径映射到下面的处理函数
def query():
    handles= request.args.get('handles').split(',')
    results=[]
    for handle in handles:
        result= solve(handle)
        results.append(result)
    return Response(json.dumps(results),mimetype='application/json')    # 返回 JSON 格式的查询结果


if __name__=='__main__':
    app.run(host='127.0.0.1',debug=True,port=2333) # Flask监听 IP地址和端口号

