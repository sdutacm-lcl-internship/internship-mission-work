from flask import Flask,request,jsonify,Response,make_response
from fake_useragent import UserAgent
import requests
import json
from datetime import timedelta,datetime
import pytz


def solve1(name):
    url="https://codeforces.com/api/user.info"
    headers={
        'User-Agent':UserAgent().random
    }
    params={
        "handles": name
    }
    try:
        response=requests.get(url=url,params=params,headers=headers)
        status_code=response.status_code
        if status_code==200:                # 此项 handle 可以查询到
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
        elif status_code==400:              # 此项 handle 无法找到
            return {
                'success':True,
                'type':1,
                'message':'no such handle'
            }
        else:                               # 在查询此项时遭遇异常 HTTP 响应
            return {
                'success':False,
                'type':2,
                'message':'HTTP response with code {}'.format(status_code),
                'datails':{
                    'status':status_code
                }
            }
    except requests.exceptions.ConnectionError or requests.exceptions.RequestException as e:    # 在查询此项时未收到有效 HTTP 响应
        return {
            'success':False,
            'type':3,
            'message':'Request timeout'
        }
    except:                                 # 在查询此项时程序发生运行时异常
        return {
            'success':False,
            'type':4,
            'message':'Internal Server Error'
        }


def solve2(name):
    url=f"https://codeforces.com/api/user.rating?handle={name}"
    headers={
        'User-Agent':UserAgent().random
    }

    try:
        response=requests.get(url=url,params=name,headers=headers)
        status_code=response.status_code
        ans=[]
        if status_code==200:
            Json=json.loads(response.text)
            user=Json['result']
            for date in user:
                ratingUpdateTime=date['ratingUpdateTimeSeconds']
                time=datetime.fromtimestamp(ratingUpdateTime, pytz.timezone('Asia/Shanghai'))
                ratingUpdateAt=time.isoformat()
                result={
                    'handle':date['handle'],
                    'contestId':date['contestId'],
                    'contestName':date['contestName'],
                    'rank':int(date['rank']),
                    'ratingUpdateAt':ratingUpdateAt,
                    'oldRating':int(date['oldRating']),
                    'newRating':int(date['newRating'])
                }
                ans.append(result)
            return ans
        elif status_code==400:
            return {
                'message':'no such handle'
            }
        else:
            return {
                'message':'HTTP response with code {}'.format(status_code)
            }
    except requests.exceptions.ConnectionError or requests.exceptions.RequestException as e:
            return {
                'message': 'Request timeout',
            }
    except:
        return {
            'message': 'Internal Server Error'
        }

app= Flask(__name__)
@app.route('/batchGetUserInfo')
def get1():
    handles=request.args.get('handles').split(',')
    results=[]
    for handle in handles:
        result =solve1(handle)
        results.append(result)
    return Response(json.dumps(results),mimetype='application/json')

@app.route('/getUserRatings')
def get2():                             #单用户查询接口
    handle = request.args.get('handle')
    result = []
    result = solve2(handle)
    return Response(json.dumps(result), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333, debug=True)
