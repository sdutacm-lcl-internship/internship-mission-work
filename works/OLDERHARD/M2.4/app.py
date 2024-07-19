from flask import Flask,request,jsonify,Response
from fake_useragent import UserAgent
import requests
import json
from datetime import timedelta,datetime
import pytz

map_user={}
map_rating={}


def solve1(name):
    if name in map_user and map_user[name]['time']>datetime.now():
        return map_user[name]['date']

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
                date={
                    'success':True,
                    'result':{
                        'handle':user['handle'],
                        'rating':int(user['rating']),
                        'rank':user['rank']
                    }
                }
            else:
                date={
                    'success':True,
                    'result':{
                        'handle':user['handle']
                    }
                }
        elif status_code==400:
            date={
                'success':True,
                'type':1,
                'message':'no such handle',
            }
        else:
            date={
                'success':False,
                'type':2,
                'message':'HTTP response with code {}'.format(status_code),
                'datails':{
                    'status':status_code
                }
            }
        map_user[name]={
            'date':date,
            'time':datetime.now()+timedelta(seconds=15)
        }
        return date
    except requests.exceptions.ConnectionError or requests.exceptions.RequestException as e:
        return {
            'success':False,
            'type':3,
            'message':'Request timeout'
        }
    except:
        return {
            'success':False,
            'type':4,
            'message':'Internal Server Error'
        }

def solve2(name):
    if name in map_rating and map_rating[name]['time']>datetime.now():
        return map_rating[name]['date']

    url=f"https://codeforces.com/api/user.rating?handle={name}"
    headers={
        'User-Agent': UserAgent().random
    }
    params={
        'handles': name
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
                    'handle':date['handle'],
                    'contestId':date['contestId'],
                    'contestName':date['contestName'],
                    'rank':int(date['rank']),
                    'ratingUpdateAt':ratingUpdateAt,
                    'oldRating':date['oldRating'],
                    'newRating':date['newRating']
                }
                ans.append(result)
        elif status_code==400:
            ans={
                'message':'no such handle'
            }
        else:
            ans={
                'message':'HTTP response with code {}'.format(status_code)
            }
        map_rating[name]={
            'date':ans,
            'time':datetime.now()+timedelta(seconds=15)
        }
        return ans
    except requests.exceptions.ConnectionError or requests.exceptions.RequestException as e:
        return {
            'message':'Request timeout'
        }
    except:
        return {
            'message':'Internal Server Error'
        }

def solve3(response):
    ans={
        'message':'invalid request'
    }
    status_code=200
    try:
        for key in response.keys():
            if key!='cacheType' and key!='handles':     #参数不符合请求体的数据结构定义
                status_code=400
                return ans,status_code
        if not 'cacheType' in response:
            status_code=400
            return ans,status_code
        if response['cacheType']!='userInfo' and response['cacheType']!='userRatings':
            status_code=400
            return ans,status_code
        if response['cacheType']=='userInfo':
            if 'handles' in response:
                for handle in response['handles']:
                    if handle in map_user:
                        del map_user[handle]
            else:
                map_user.clear()
        if response['cacheType']=='userRatings':
            if 'handles' in response:
                for handle in response['handles']:
                    if handle in map_rating:
                        del map_rating[handle]

            else:
                map_rating.clear()
        ans['message']='ok'
    except requests.exceptions.RequestException as e:
        status_code=400
    except Exception as e:
        status_code=500
        ans['message']='invalid Server Error'
    return ans,status_code


app=Flask(__name__)

@app.route('/batchGetUserInfo')
def get1():
    handles=request.args.get('handles').split(',')
    results=[]
    for handle in handles:
        result=solve1(handle)
        results.append(result)
    return Response(json.dumps(results),mimetype='application/json')

@app.route('/getUserRatings')
def get2():
    handle=request.args.get('handle')
    result=[]
    result=solve2(handle)
    return Response(json.dumps(result),mimetype='application/json')

@app.route('/clearCache',methods=['POST'])
def clear_cache():
    if request.content_type=='application/json':
        response=request.json
        ans=solve3(response)
        return jsonify(ans[0]),ans[1]
    elif request.content_type=='application/x-www-form-urlencoded':
        response=request.form
        if 'handles' in response:       # 4种情况，handles,handles[],handles[0],无
            list=response.getlist('handles')
            response=json.loads(json.dumps(response))
            response['handles']=list
        elif 'hanles[]' in response:
            list=response.getlist('handles[]')
            response=json.loads(json.dumps(response))
            del response['handles[]']
            response['handles']=list
        elif 'hanles[0]' in response:
            cnt=0
            res={}
            list=[]
            for key,value in response.items():
                if key=='handles['+str(cnt)+']':
                    list.append(value)
                    cnt +=1
                else:
                    res[key]=value
            if len(list)!=0:
                res['handles']=list
            response=json.loads(json.dumps(res))
        else:
            response=json.loads(json.dumps(response))
        ans=solve3(response)
        return jsonify(ans[0]),ans[1]

if __name__=='__main__':
    app.run(host='127.0.0.1',port=2333,debug=True)
