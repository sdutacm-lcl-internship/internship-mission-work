from flask import Flask,request,jsonify,Response
from fake_useragent import UserAgent
import requests
import json
from datetime import timedelta,datetime
import pytz


def solve1(name):

    url='https://codeforces.com/api/user.info'
    headers={
        'User-Agent':UserAgent().random
    }
    params={
        'handles':name
    }
    try:
        response=requests.get(url=url,params=params,headers=headers)
        status_code=response.status_code
        if status_code==200:
            Json=json.loads(response.text)
            user=Json['result'][0]
            if 'rating' in user:
                ans={
                    'success':True,
                    'result':{
                        'handle':user['handle'],
                        'rating':int(user['rating']),
                        'rank':user['rank']
                    }
                }
            else:
                ans={
                    'success':True,
                    'result':{
                        'handle':user['handle']
                    }
                }
            return ans
        elif status_code==400:
            ans={
                'success':True,
                'type':1,
                'message':'no such handle'
            }
            return ans
        else:
            ans={
                'success':False,
                'type':2,
                'message':'HTTP response with code {}'.format(status_code),
                'details':{
                    'status':status_code
                }
            }
            return ans
    except requests.exceptions.ConnectionError or requests.exceptions.RequestException as e:
        ans={
            'success':False,
            'type':3,
            'message':'Request timeout'
        }
        return ans
    except:
        ans={
            'success':False,
            'type':4,
            'message':'Internal Servel Error'
        }
        return ans

def find1(name):
    try:
        with open('user_info','r') as f:        # 如果存在，尝试打开
            cache_date=json.load(f)
            deadline=datetime.fromtimestamp(cache_date['deadline'])
            if  cache_date['name']==name and deadline>datetime.now():
                return cache_date['date']
    except:
        pass
    date=solve1(name)
    deadline=datetime.now()+timedelta(seconds=30)
    cache_date={
        'deadline':deadline.isoformat(),
        'date':date,
        'name':name
    }
    with open('user_info','w') as f:
        json.dump(cache_date,f)
    return date

def solve2(name):

    url=f"https://codeforces.com/api/user.rating?handle={name}"
    headers={
        'User_Agent':UserAgent().random
    }
    params={
        'handles':name
    }
    try:
        response=requests.get(url=url,params=params,headers=headers)
        status_code=response.status_code
        if status_code==200:
            Json=json.loads(response.text)
            user=Json['result']
            ans=[]
            for date in user:
                ratingUpdateTime=date['ratingUpdateTimeSeconds']
                time=datetime.fromtimestamp(ratingUpdateTime,pytz.timezone('Asia/Shanghai'))
                ratingUpdateAt=time.isoformat()
                result={
                    'handle': date['handle'],
                    'contestId': date['contestId'],
                    'contestName': date['contestName'],
                    'rank': int(date['rank']),
                    'ratingUpdateAt': ratingUpdateAt,
                    'oldRating': int(date['oldRating']),
                    'newRating': int(date['newRating'])
                }
                ans.append(result)
            return ans
        elif status_code==400:
            ans={
                'message':'no such handle'
            }
            return ans
        else:
            ans={
                'message':'HTTP response with code {}'.format(status_code)
            }
            return ans
    except requests.exceptions.ConnectionError or requests.exceptions.RequestException as e:
        ans={
            'message':'Request timeout'
        }
        return ans
    except:
        ans={
            'message':'Internal Server Error'
        }
        return ans

def find2(name):
    try:
        with open('user_rating','r') as f:      #如果存在，尝试打开
            cache_date=json.load(f)
            deadline=datetime.fromtimestamp(cache_date['deadline'])
            if cache_date['name']==name and deadline > datetime.now():
                return cache_date['date']
    except:
        pass
    date=solve2(name)
    deadline=datetime.now()+timedelta(seconds=30)
    cache_date={
        'deadline':deadline.isoformat(),
        'date':date,
        'name':name
    }
    with open('user_rating','w') as f:
        json.dump(cache_date,f)
    return date

app=Flask(__name__)

@app.route('/batchGetUserInfo')
def get1():
    handles=request.args.get('handles').split(',')
    results=[]
    for handle in handles:
        result=find1(handle)
        results.append(result)
    return Response(json.dumps(results),mimetype='application/json')

@app.route('/getUserRatings')
def get2():
    handle=request.args.get('handle')
    result=find2(handle)
    return Response(json.dumps(result),mimetype='application/json')

if __name__=='__main__':
    app.run(host='127.0.0.1',port=2333,debug=True)
