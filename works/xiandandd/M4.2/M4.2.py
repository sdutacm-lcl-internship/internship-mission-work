import sqlite3
import pandas as pd
import os
import openpyxl
from flask import Flask, jsonify
import copy
from flask import Flask, request, jsonify, Response
import requests
from datetime import datetime
import pytz
from flask import Flask, request, jsonify,g
import threading
from werkzeug.datastructures import MultiDict
from flask import render_template
# 获取数据库连接
def get_db():
    db = getattr(g, '_database', None)

    if db is None:
        db = g._database = sqlite3.connect("cf.db")
        db.execute("PRAGMA foreign_keys = ON")
    return db
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
# 初始化数据库
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        cursor.execute('''
               CREATE TABLE IF NOT EXISTS user_info (
                   handle VARCHAR PRIMARY KEY NOT NULL,
                   rating INT,
                   rank VARCHAR,
                   updated_at DATETIME NOT NULL
               );
           ''')

        # 创建表 user_rating
        cursor.execute('''
               CREATE TABLE IF NOT EXISTS user_rating (
                   user_rating_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                   handle VARCHAR NOT NULL,
                   contest_id INT NOT NULL,
                   contest_name VARCHAR NOT NULL,
                   rank INT NOT NULL,
                   old_rating INT NOT NULL,
                   new_rating INT NOT NULL,
                   rating_updated_at DATETIME NOT NULL,
                   updated_at DATETIME NOT NULL,
                   FOREIGN KEY (handle) REFERENCES user_info(handle)
               ); 
           ''')

        db.commit()

#获取rating表中的最后一条数据的id值
def findlastid():
    db=get_db()
    cursor=db.cursor()
    cursor.execute("SELECT user_rating_id FROM user_rating ORDER BY user_rating_id DESC LIMIT 1")
    p=cursor.fetchone()
    if p is not None:
        return p[0]
    else:
        return None

# 插入数据
def insertinfo(handle, rating, rank, updated_at):
    db=get_db()
    cursor=db.cursor()
    cursor.execute("INSERT INTO user_info (handle, rating, rank, updated_at) VALUES (?, ?, ?, ?)", (handle, rating, rank, updated_at))
    db.commit()
def insertratig(id,handle,contest_id,name,rank,old_rating,new_rating,time,updated_at):
    db=get_db()
    cursor=db.cursor()
    try:
        cursor.execute(
            "INSERT INTO user_rating(user_rating_id, handle, contest_id, contest_name, rank, old_rating, new_rating, rating_updated_at, updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (id, handle, contest_id, name, rank, old_rating, new_rating, time, updated_at))
        db.commit()
        return
    except sqlite3.IntegrityError as e:
        #如果不加这句话就会报错，显示表格被锁定了
        db.commit()
        handles=[]
        handles.append(handle)
        query_handles(handle)
        cursor.execute(
            "INSERT INTO user_rating(user_rating_id, handle, contest_id, contest_name, rank, old_rating, new_rating, rating_updated_at, updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
            (id, handle, contest_id, name, rank, old_rating, new_rating, time, updated_at))
        db.commit()
        return
# 查询数据
def findinfo(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user_info WHERE handle=?", (username,))
    rows = cursor.fetchall()
    db.commit()
    return rows
def findrating(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user_rating WHERE handle=?", (username,))
    rows = cursor.fetchall()
    db.commit()
    return rows
def findallinfo():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user_info")
    rows = cursor.fetchall()
    db.commit()
    return rows
def findallrating():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user_rating")
    rows = cursor.fetchall()
    db.commit()
    return rows
def deleteinfo(username):
    db=get_db()
    cursor=db.cursor()
    cursor.execute("DELETE FROM user_info where handle = ?",(username,))
    db.commit()
    return
def deleterating(username):
    db=get_db()
    cursor=db.cursor()
    cursor.execute("DELETE FROM user_rating where handle = ?",(username,))
    db.commit()
    return
def updateinfo(username,rating,rank,updated_at):
    db=get_db()
    cursor=db.cursor()
    cursor.execute("update user_info set handle=?,rating=?,rank=?,updated_at=? where handle=?",(username,rating,rank,updated_at,username))
    db.commit()
    return
def updaterating(id,handle,contest_id,name,rank,old_rating,new_rating,time,updated_at):
    db=get_db()
    cursor=db.cursor()
    cursor.execute("update user_rating set user_rating_id=?,handle=?,contest_id=?,contest_name=?,rank=?,old_rating=?,new_rating=?,rating_updated_at=?,updated_at=? where user_rating_id=?)",(id,handle,contest_id,name,rank,old_rating,new_rating,time,updated_at,id))
    db.commit()
    return
def process(data):
    res = {}
    for key, value in data.items():
        if '.' in key:
            subkeys = key.split('.')
            subdict = res
            for subkey in subkeys[:-1]:
                if subkey not in subdict:
                    subdict[subkey] = {}
                subdict = subdict[subkey]
            subdict[subkeys[-1]] = value
        else:
            res[key] = value
    return res

ratingid=0


app = Flask(__name__)

# 设置Application/X-WWW-Form-UrlEncoded请求体解析器
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
# rating = {}
# info = {}

#清除缓存
# @app.route('/clearCache', methods=['POST'])
# def clear_cache():
#     # 解析请求参数
#     global info, rating
#     if request.headers['Content-Type'].startswith('application/json'):
#         data=request.get_json()
#         type=data.get('cacheType',None)
#         if "handles" not in data:
#             handles=[]
#         else:
#             handles=data.get('handles')
#     elif request.headers['Content-Type'].startswith('application/x-www-form-urlencoded'):
#         data = request.form
#
#         type=data.get('cacheType',None)
#         if "handles" not in data:
#             handles=[]
#         else:
#             handles = data.getlist('handles')
#     else:
#         ans = {
#             'result': {
#                 'message': 'invalid request'
#             },
#             'status': 400
#         }
#         return jsonify(ans["result"]), ans["status"]
#     if type not in ['userInfo', 'userRatings']:
#         ans = {
#             'result': {
#                 'message': 'invalid request',
#             },
#             'status': 400
#         }
#         return jsonify(ans["result"]), ans["status"]
#
#
#     if type == 'userInfo':
#         total = copy.deepcopy(info)
#     else:
#         total = copy.deepcopy(rating)
#     if handles == []:
#         total = {}
#     else:
#         for handle in handles:
#             if handle in total:#当请求体中handle存在的时候，才会pop掉，否则会key error
#
#                 total.pop(handle)
#     #再把字典传递回去
#     if type == 'userInfo':
#         info = copy.deepcopy(total)
#     else:
#         rating = copy.deepcopy(total)
#     # 返回成功响应
#     return jsonify({'message': 'ok'}),200

#用户信息查询
def solve(username):
    url = "https://codeforces.com/api/user.info"
    # 请求的handles参数
    params = {
        "handles": username
    }

    try:
        # 1/0
        # 新建一个空的response对象，以便于异常的判断
        response = requests.Response()
        response = requests.get(url, params=params)
        number = response.status_code

        data = response.json()
        # 没有收到响应的情况
        if response is None:
            user_info = {
                "success": False,
                "type": 3,
                "message": "No valid HTTP response was received when querying this item",
            }
            return user_info
        # 遇到异常http响应的情况,408是Request Timeout，504是Gateway Timeout
        elif number == 404 or number == 503 or number == 403 or number == 500 or number == 408 or number == 504:
            user_info = {
                "success": False,
                "type": 2,
                "message": data["comment"],
                "details": {
                    "status": number,
                }
            }
            return user_info
        # 前面写了没有响应的情况，这里再特判一下极小概率的情况
        elif "Content-Type" not in response.headers:
            user_info = {
                "success": False,
                "type": 3,
                "message": "No valid HTTP response was received when querying this item",
            }
            return user_info
        if data["status"] == "OK":
            for user in data["result"]:
                # 查看rank这个键是否存在，若不存在那么就是没用rating的用户
                if "rank" not in user:
                    user_info = {
                        "success": True,
                        "result": {
                            "handle": user['handle'],
                        }
                    }
                else:
                    user_info = {
                        "success": True,
                        "result": {
                            "handle": user["handle"],
                            "rating": user["rating"],
                            "rank": user["rank"]
                        }
                    }
                return user_info
        # 因为前面把错误的状态码都筛选掉了，所以剩下的就是查无此人的情况了
        elif data["status"] == "FAILED":
            user_info = {
                "success": False,
                "type": 1,
                "message": 'no such handle'
            }
            return user_info
    # 发现如果访问api失败也会收到状态码，这种情况下一般是503的状况
    # 访问失败，没有收到状态码就是断网的情况了
    except requests.exceptions.RequestException as e:
        if response is not None and response.status_code != 200 and response.status_code != 400:
            user_info = {
                "success": False,
                "type": 2,
                "message": "Abnormal response",
                "details": {
                    "status": response.status_code,
                }
            }
        # 断网了，没有收到响应
        else:
            user_info = {
                "success": False,
                "type": 3,
                "message": "No valid HTTP response was received when querying this item",
            }
        return user_info
    # 这是程序异常的情况
    except:
        user_info = {
            "success": False,
            "type": 4,
            "message": "Internal Server Error"
        }
        return user_info

#用户信息查询路由
@app.route('/batchGetUserInfo', methods=['GET'])
def query():
    handles = request.args.get('handles')
    return query_handles(handles)
def query_handles(handles):
    # 获取handles
    # 将handles按逗号分割成列表
    handle_list = handles.split(',')
    response_data = []

    for handle in handle_list:
        if isinfo(handle):
            info=findinfo(handle)
            infos=info[0]
            if infos[1] is None:
                p={
                    'result':{
                        'handle':infos[0]
                    },
                    'success':True,
                }
            else:
                p = {
                    'result': {
                        'handle': infos[0],
                        'rating':infos[1],
                        'rank':infos[2]
                    },
                    'success': True,
                }
            response_data.append(p)

        else:
            value = solve(handle)
            f=findinfo(handle)
            if 'result' in value:
                if 'rating' in value['result']:
                    rating = value['result'].get('rating')
                else:
                    rating=None
                if 'rank' in value['result']:
                    rank=value['result'].get('rank')
                else:
                    rank=None
            else:
                rating = None
                rank = None
            if value['success'] is True:
                f=findinfo(handle)
                if f==[]:
                    insertinfo(handle, rating, rank, datetime.now())
                else:
                    updateinfo(handle,rating,rank,datetime.now())
            response_data.append(value)

    # jsonify()函数简化了将数据转换为JSON响应的过程，并确保响应的Content-Type标头正确设置为application/json
    # 这样，浏览器或其他客户端会正确地解析返回的JSON数据了

    return jsonify(response_data)


# 记录查询函数体
def find(username):
    url = 'https://codeforces.com/api/user.rating'
    params = {
        'handle': username,
    }
    try:
        response = requests.get(url=url, params=params)
        number = response.status_code
        if number == 200:
            data = response.json()
            for one in data["result"]:
                dt = datetime.fromtimestamp(one["ratingUpdateTimeSeconds"], pytz.timezone('Asia/Shanghai'))
                dtstring = dt.isoformat()

                one["ratingUpdatedAt"] = dtstring
                one.pop("ratingUpdateTimeSeconds")  # 把原来的时间戳键值删掉
            data["status"] = 200
            return data
        elif number == 400:
            data = {
                'status': 404,
                "result": {
                    "message": 'no such handle',
                }
            }
            return data
        else:
            data = {
                'status': number,
                "result": {
                    "message": 'Abnormal response',
                }
            }
            return data
    except requests.exceptions.RequestException as e:
        data = {
            'status': 503,
            "result": {
                "message": 'Connection interruption',
            }
        }
        return data
    except:
        data = {
            'status': 500,
            "result": {
                "message": 'program exception',
            }
        }
        return data


# 单用户查询用户记录
@app.route('/getUserRatings', methods=['GET'])
def getUserRatings():
    handle = request.args.get('handle')
    if israting(handle):
        find_list=findrating(handle)
        ps={
            'result':[],
            'status':200,
        }
        for finds in find_list:
            p={
                "handle": handle,
                "contestId": finds[2],
                "contestName": finds[3],
                "rank": finds[4],
                "ratingUpdatedAt": finds[-2],
                "oldRating": finds[-4],
                "newRating": finds[-3],
            }
            ps['result'].append(p)
            find_list=ps
    else:
        find_list = find(handle)
        if find_list['status'] ==200:
            values=find_list['result']
            for value in values:
                ratingid=findlastid()
                if ratingid is None:
                    ratingid=0
                else:
                    ratingid=ratingid+1
                insertratig(ratingid, handle, value['contestId'], value['contestName'], value['rank'], value['oldRating'],
                            value['newRating'], value['ratingUpdatedAt'],datetime.now())

    # jsonify函数返回的是一个response对象，所以可以在后面直接加状态码
    return jsonify(find_list["result"]), find_list["status"]

#判断比赛记录是否存在
def israting(username):
    ratings=findallrating()
    for rating in ratings:
        if username in rating:
            nowtime = datetime.now()
            lefttime = rating[-1]
            datetime_format = "%Y-%m-%d %H:%M:%S.%f"
            times = datetime.strptime(lefttime, datetime_format)
            t = (nowtime - times).total_seconds()
            if t < 30:
                return True
            else:
                #因为这里如果是用update的话就比较麻烦了，所以我只在查询info的时候使用update，
                deleterating(username)
                return False
    else:
        return False

#判断个人信息是否存在缓存
def isinfo(username):
    infos=findallinfo()
    for info in infos:
        if username in info:
            nowtime = datetime.now()
            lefttime = info[3]
            datetime_format = "%Y-%m-%d %H:%M:%S.%f"
            times = datetime.strptime(lefttime, datetime_format)
            t = (nowtime - times).total_seconds()
            if t < 30:
                return True
            else:
                return False
    return False



@app.route('/', methods=['GET'])
def ooo():
    return render_template('p.html')

if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=2333)
