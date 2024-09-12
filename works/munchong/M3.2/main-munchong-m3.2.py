import json
import time
import pytz
import sqlite3
import requests
import datetime
from fake_useragent import UserAgent
from flask import Flask, request, Response, render_template

app = Flask(__name__)


if __name__ == '__main__':
    app.run()


app = Flask(__name__)


# 链接数据库建表
def init_database():
    # 链接数据库 如果没有将创建此库
    conn = sqlite3.connect('codeforces.db')
    # 建立游标
    c = conn.cursor()

    # 确定此时是否表存在 不存在则创建
    table_name = 'user_info'
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if c.fetchone() is None:
        # 创建 user_info 表
        print("ok-one")
        c.execute('''CREATE TABLE user_info
                     (handle VARCHAR PRIMARY KEY NOT NULL,
                      rating INT,
                      rank VARCHAR,
                      updated_at DATETIME NOT NULL)''')

    table_name = 'user_rating'
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if c.fetchone() is None:
        # 创建 user_info 表
        print("ok-two")
        c.execute('''CREATE TABLE user_rating
                     (user_rating_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                      handle VARCHAR NOT NULL,
                      contest_id INT NOT NULL,
                      contest_name VARCHAR NOT NULL,
                      rank INT NOT NULL,
                      old_rating INT NOT NULL,
                      new_rating INT NOT NULL,
                      rating_updated_at DATETIME NOT NULL,
                      updated_at FLOAT NOT NULL,
                      FOREIGN KEY (handle) REFERENCES user_info (handle))''')
    # 提交更改并关闭连接
    conn.commit()
    conn.close()


# 爬虫获得对应的数据Info并存入数据库
def get_information(nickname):
    # 准备好要更新的数据
    print(nickname)
    handle = nickname
    rating = 0
    rank = 'no'

    # 调用程序获取信息的模块
    try:
        e_url = f"https://codeforces.com/api/user.info"
        params = {"handles": nickname}
        response = requests.get(e_url, params=params)
        data = json.loads(response.text)

        if response.status_code == 200:
            # 查无此人
            if data["status"] == "FAILED":
                ans = {
                    "success": "False",
                    "type": 1,
                    "message": "no such handle"
                }
            # 无rank
            elif data["result"][0]["contribution"] == 0:
                ans = {
                    "success": "False",
                    "result": {
                        "handle": nickname
                    }
                }
            # 一切正常
            else:
                ans = {
                    "success": "True",
                    "result": {
                        "handle": data["result"][0]["handle"],
                        "rating": data["result"][0]["rating"],
                        "rank": data["result"][0]["rank"]
                    }
                }
                rank = data["result"][0]["rank"]
                rating = data["result"][0]["rating"]
        # 响应错误
        elif response.status_code == 401 or response.status_code == 402 or response.status_code == 403 or \
            response.status_code == 404 or response.status_code == 405 or response.status_code == 501 or \
            response.status_code == 502 or response.status_code == 503 or response.status_code == 504 or \
            response.status_code == 400:
            ans = {
                "success": "False",
                "type": 2,
                "message": "Http response with code" + str(response.status_code),
                "details": {
                    "status": response.status_code
                }
            }
        # 无效响应
        else:
            ans = {
                "success": "False",
                "type": 3,
                "message": "No legitimate response was received"
            }
    except:
        # 本身程序异常
        ans = {
            "success": "False",
            "type": 4,
            "message": "Program error"
        }
    if ans['success'] == "True":
    # 如果查询成功的话就更新写入
        # 链接数据库 建立游标
        conn = sqlite3.connect('codeforces.db')
        c = conn.cursor()

        # 向user_info表中插入数据
        updated_at = datetime.datetime.now()
        c.execute("INSERT INTO user_info (handle, rating, rank, updated_at) VALUES (?, ?, ?, ?)",
                  (handle, rating, rank, updated_at))
        print(f"{c.rowcount} rows inserted into user_info table")
        # 提交更改并关闭连接
        conn.commit()
        conn.close()

    return ans


# 处理GetUserInfo的相关请求并处理
@app.route('/batchGetUserInfo', methods=['GET'])
def solve():
    init_database()
    handle = request.args.get('handles')
    answer_message = []

    # 先数据库中经行查找
    conn = sqlite3.connect('codeforces.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_info WHERE handle=?", (handle,))
    result = c.fetchone()

    # 如果有而且时间合适的话
    if result is not None and time.time() - result["updated_at"] < 30:
        if result["rank"] is not None:
            ans = {
                "success": "True",
                "result": {
                    "handle": handle,
                    "rating": result["rating"],
                    "rank": result["rank"]
                }
            }
            answer_message.append(ans)
        else:
            ans = {
                "success": "True",
                "result": {
                    "handle": handle,
                }
            }
            answer_message.append(ans)
    else:
    # 否则重写一把
        answer_message.append(get_information(handle))
    return Response(json.dumps(answer_message), mimetype="application/json")


# 爬虫获得 对应的数据 Info
def get_UserRating_two(nickname):
    try:
        e_url = f"https://codeforces.com/api/user.rating?handle={nickname}"
        response = requests.get(url=e_url)
        data = json.loads(response.text)

        ans = []
        if response.status_code == 200:
            conn = sqlite3.connect('codeforces.db')
            c = conn.cursor()
            for every_thing in data['result']:
                dt = datetime.datetime.fromtimestamp(every_thing['ratingUpdateTimeSeconds'],
                                                     pytz.timezone('Asia/Shanghai'))
                dtt = dt.isoformat()
                roww = {
                    "handle": every_thing['handle'],
                    "contestId": every_thing["contestId"],
                    "contestName": every_thing['contestName'],
                    "rank": every_thing['rank'],
                    "ratingUpdatedAt": dtt,
                    "oldRating": every_thing['oldRating'],
                    "newRating": every_thing['newRating'],
                }
                # print(roww['contestId'])
                handle = roww['handle']
                contest_id = roww['contestId']
                contest_name = roww['contestName']
                rank = roww['rank']
                old_rating = roww['oldRating']
                new_rating = roww['newRating']
                rating_updated_at = dtt
                updated_at = time.time()
                print('*')
                print(updated_at)
                c.execute(
                    "INSERT INTO user_rating (handle, contest_id, contest_name, rank, old_rating, new_rating, "
                    "rating_updated_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (handle, contest_id, contest_name, rank, old_rating, new_rating, rating_updated_at, updated_at))
                print(f"{c.rowcount} rows inserted into user_rating table")
                ans.append(roww)
            conn.commit()
            conn.close()
        elif response.status_code == 400:
            # 查无此人
            ans = {"message": "no such handle"}
        elif response.status_code == 401 or response.status_code == 402 or response.status_code == 403 or \
            response.status_code == 405 or response.status_code == 501 or response.status_code == 502 or \
            response.status_code == 503 or response.status_code == 504:
            # 响应错误
            ans = {"message": "Http response with code" + str(response.status_code)}
        else:
            # 无效响应
            ans = {"message": "No legitimate response was received"}
    except:
        # 本身程序异常
        ans = {"message": "Program error"}
    return ans


# 获取 rating 的信息 开始判断
@app.route('/getUserRatings', methods=['GET'])
def getUserRatings():
    init_database()
    handle = request.args.get('handle')
    answer_message = []

    #链接数据库查询
    conn = sqlite3.connect('codeforces.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_rating WHERE handle=?", (handle,))
    it = c.fetchall()
    if it is not None and len(it) != 0:
        for row in it:
            print(time.time())
            # for now in range(0, 9):
            #     print(now)
            #     print(row[now])
            # print(abs(time.time() - float(row[8])))
            if abs(time.time() - float(row[8])) < 30:
                ans = {
                    "handle": row[0],
                    "contestId": row[1],
                    "contestName": row[2],
                    "rank": row[3],
                    "ratingUpdatedAt": row[4],
                    "oldRating": row[5],
                    "newRating": row[6],
                }
                answer_message.append(ans)

    else:
        roww = get_UserRating_two(handle)
        answer_message.append(roww)
    conn.close()
    return Response(json.dumps(answer_message), mimetype="application/json")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=2333, debug=True)




