from flask import Flask,request,jsonify,Response
from fake_useragent import UserAgent
import requests
import json
from datetime import timedelta,datetime
import pytz
import sqlite3


def sqlite_user_info(handle,rating,rank):
    with sqlite3.connect('cf.db') as conn:
        cursor=conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")  #将外键约束打开
        now = datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()
        cursor.execute('''
        INSERT OR REPLACE INTO
        user_info(handle,rating,rank,updated_at)
        VALUES(?,?,?,?)''',(handle,rating,rank,now))
        conn.commit()   #提交事务

def sqlite_user_rating(handle,contestId,contestName,rank,oldRating,newRating,ratingUpdatedAt):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")  #将外键约束打开
        now = datetime.now(pytz.timezone('Asia/Shanghai')).isoformat()
        cursor.execute('''
        SELECT handle FROM user_info WHERE handle = ?
        ''',(handle,))
        date=cursor.fetchone()  #获取查询结果的第一行数据
        if date is None:
            solve1(handle)
        cursor.execute('''
        INSERT OR REPLACE INTO 
        user_ratings(handle,contest_id,contest_name,rank,old_rating,new_rating,rating_updated_at,updated_at)
        VALUES(?,?,?,?,?,?,?,?)''',(handle,contestId,contestName,rank,oldRating,newRating,ratingUpdatedAt,now))
        conn.commit()   #提交事务
def solve1(name):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        sub=(datetime.now(pytz.timezone('Asia/Shanghai'))-timedelta(seconds=30)).isoformat()
        cursor.execute('''
        SELECT rating,rank
        FROM user_info 
        WHERE handle = ? AND updated_at > ?''',(name,sub))
        res=cursor.fetchone()   #获取查询结果的第一行数据
        if res:
            rating,rank=res
            if rating and rank:
                result={
                    'handle':name,
                    'rating':rating,
                    'rank':rank
                }
            else:
                result={
                    'handle':name
                }
            ans={
                'success':True,
                'result':result
            }
            return ans
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
                sqlite_user_info(user['handle'],user['rating'],user['rank'])
                conn.close()
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

def solve2(name):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        sub = (datetime.now(pytz.timezone('Asia/Shanghai')) - timedelta(seconds=30)).isoformat()
        cursor.execute('''
        SELECT contest_id,contest_name,rank,old_rating,new_rating,rating_updated_at
        FROM user_ratings
        WHERE handle =? AND updated_at > ?
        ''',(name,sub))
        res=cursor.fetchall()   #获取查询结果的所有行数据
        if res:
            ans=[]
            for date in res:
                contest_id,contest_name,rank,oldrating,newrating,ratingUpdatedAt= date
                result={
                    'handle':name,
                    'contestId':contest_id,
                    'contestName':contest_name,
                    'rank':rank,
                    'ratingUpdatedAt':ratingUpdatedAt,
                    'oldrating':oldrating,
                    'newrating':newrating
                }
                ans.append(result)
            return ans

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
                ratingUpdatedAt=time.isoformat()
                result={
                    'handle': date['handle'],
                    'contestId': date['contestId'],
                    'contestName': date['contestName'],
                    'rank': int(date['rank']),
                    'ratingUpdatedAt': ratingUpdatedAt,
                    'oldRating': int(date['oldRating']),
                    'newRating': int(date['newRating'])
                }
                ans.append(result)
                sqlite_user_rating(date['handle'],date['contestId'],date['contestName'],int(date['rank']),int(date['oldRating']),int(date['newRating']),ratingUpdatedAt)
            conn.close()
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

def creat():
    with sqlite3.connect('cf,db') as conn:
        cursor=conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_info(
        handle VARCHAR PRIMARY KEY NOT NULL,
        rating INT,
        rank VARCHAR,
        updated_at DATETIME NOT NULL
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_ratings(
        user_rating_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        handle VARCHAR NOT NULL,
        contest_id INT NOT NULL,
        contest_name VARCHAR NOT NULL,
        rank INT NOT NULL,
        old_rating INT NOT NULL,
        new_rating INT NOT NULL,
        rating_updated_at DATETIME NOT NULL,
        updated_at DATETIME NOT NULL,
        FOREIGN KEY (handle) REFERENCES user_info (handle),
        UNIQUE(handle,contest_id) ON CONFLICT REPLACE
        )
        ''')
    conn.commit()

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
    result=solve2(handle)
    return Response(json.dumps(result),mimetype='application/json')

if __name__=='__main__':
    creat()
    app.run(host='127.0.0.1',port=2333,debug=True)
