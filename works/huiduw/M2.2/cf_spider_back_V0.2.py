from flask import Flask,request,jsonify
import requests
import json
import sys
app = Flask(__name__) #创建实例

#错误信息
ERROR_MESSAGES = {
    "1": "no such handle",
    "2": "No valid HTTP response was received",
    "3": "Abnormal HTTP response",
    "4": "Internal Server Error"
}


def get_user_info(username):
    url = "https://codeforces.com/api/user.info"
    # 配置参数
    params = {
        "handles": username
    }

    res = requests.get(url,params)
    status = res.status_code
    info_json = res.json()

    if status == 200 or status == 400:
        if info_json["status"] == "OK":
            for user in info_json["result"]:
                if "rank" not in user:
                    user_info = {"handle": params["handles"]}
                else:
                    user_info = {
                        "handle": params["handles"],
                        "rating": user["rating"],
                        "rank": user["rank"]
                    }
                user_json = json.dumps(user_info)
                res_json = {
                    "success": True,
                    "result": user_json
                }
                return res_json
        elif info_json["status"] == "FAILED":
            res_json = {
                "success": False,
                "message": ERROR_MESSAGES['1']
            }
            return res_json
    elif status == 404: #状态码404 未收到有效HTTP响应
        res_json = {
            "success": False,
            "message": ERROR_MESSAGES['2']
        }
        return res_json
    elif status // 100 == 4: #状态码4xx 异常HTTP响应
        res_json = {
            "success": False,
            "message": ERROR_MESSAGES['3']
        }
        return res_json
    elif status // 100 == 5: #状态码5xx 服务器错误
        res_json = {
            "success": False,
            "message": ERROR_MESSAGES['4']
        }
        return res_json

@app.route('/batchGetUserInfo',methods =['GET'])
def batchGetUserInfo():
    data = []
    try:
        usernames = request.args.get('handles')
        query_list = usernames.split(',')
        for username in query_list:
             result = get_user_info(username)
             data.append(result)
    except Exception as e:
        return '传个参数先啦'
    return jsonify(data)

def get_user_rating(username):
    url = "https://codeforces.com/api/user.rating"
    # 配置参数
    params = {
        "handle": username
    }
    res = requests.get(url,params)
    status = res.status_code
    info_json = res.json()
    if status == 200 :
        rating_records = info_json["result"]
        print(rating_records)
        return rating_records
    elif status == 400:
        res_json = {
            "message" : ERROR_MESSAGES['1']
        }
        return res_json
    elif status // 100 == 4: #状态码4xx 异常HTTP响应
        res_json = {
            "message": ERROR_MESSAGES['3']
        }
        return res_json
    elif status // 100 == 5: #状态码5xx 服务器错误
        res_json = {
            "message": ERROR_MESSAGES['4']
        }
        return res_json

@app.route('/getUserRatings',methods =['GET'])
def getUserRatings():
    try:
        username = request.args.get('handle')
        result = get_user_rating(username)
        print(result)
        return result
    except Exception as e:
        return '传个参数先啦'




if __name__ == '__main__':
    app.run('127.0.0.1',port=2333) #指定提供服务的端口号

