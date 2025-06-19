from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)  # 创建实例



# 错误信息
ERROR_MESSAGES = {
    "1": "no such handle",
    "2": "No valid HTTP response was received",
    "3": "Abnormal HTTP response",
    "4": "Internal Server Error"
}

USER_INFO_SAVE = "data-user-info.json"
USER_RATING_SAVE = "data-user-rating.json"


def get_user_info(username):
    url = "https://codeforces.com/api/user.info"
    # 配置参数
    params = {
        "handles": username
    }

    res = requests.get(url, params)
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
    elif status == 404:  # 状态码404 未收到有效HTTP响应
        res_json = {
            "success": False,
            "message": ERROR_MESSAGES['2']
        }
        return res_json
    elif status // 100 == 4:  # 状态码4xx 异常HTTP响应
        res_json = {
            "success": False,
            "message": ERROR_MESSAGES['3']
        }
        return res_json
    elif status // 100 == 5:  # 状态码5xx 服务器错误
        res_json = {
            "success": False,
            "message": ERROR_MESSAGES['4']
        }
        return res_json

def get_user_rating(username):
    url = "https://codeforces.com/api/user.rating"
    # 配置参数
    params = {
        "handle": username
    }
    res = requests.get(url, params)
    status = res.status_code
    info_json = res.json()
    if status == 200:
        rating_records = info_json["result"]
        # print(rating_records)
        return rating_records
    elif status == 400:
        res_json = {
            "message": ERROR_MESSAGES['1']
        }
        return res_json
    elif status // 100 == 4:  # 状态码4xx 异常HTTP响应
        res_json = {
            "message": ERROR_MESSAGES['3']
        }
        return res_json
    elif status // 100 == 5:  # 状态码5xx 服务器错误
        res_json = {
            "message": ERROR_MESSAGES['4']
        }
        return res_json

#移除过期数据
def remove_expired_data(read_data):
    filtered_data = []
    for d in read_data:
        time_difference = datetime.now() - datetime.strptime(d['timestamp'], '%Y-%m-%d %H:%M:%S')
        if time_difference.total_seconds() <= 30:
            filtered_data.append(d)
    return filtered_data


# 定义一个函数来从文件中读取数据
def read_data_from_file(filename):
    with open(filename, 'r') as f:
        read_data = json.load(f)
        data = remove_expired_data(read_data)
    return data


# def write_data_to_file(data, filename):
#     if  os.path.exists(filename):
#         original_data = read_data_from_file(filename)
#         new_data = original_data + data
#         with open(filename, 'w') as f:
#             json.dump(new_data, f)
#     else :
#         with open(filename, 'w') as f:
#             json.dump(data,f)

# 定义一个函数来将数据写入文件
def write_data_to_file(data, filename):
    if os.path.exists(filename):
        original_data = read_data_from_file(filename)
        new_data = original_data.copy()
        for d in data:
            d['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_data.extend(data)
        with open(filename, 'w') as f:
            json.dump(new_data, f)
    else:
        for d in data:
            d['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(filename, 'w') as f:
            json.dump(data, f)

#对爬取的用户信息数据进行读写
def get_info_data(query_list):
    data = []
    # 首先检查文件是否存在
    if not os.path.exists(USER_INFO_SAVE):
        # 文件不存在，进行爬取和写入操作
        for username in query_list:
            result = get_user_info(username)
            if result:
                data.append(result)
        # 将json数据写入文件
        write_data_to_file(data, USER_INFO_SAVE)
    else:
        # 首先从文件中读取数据
        read_data = read_data_from_file(USER_INFO_SAVE)
        stored_handles = []
        for item in read_data:
            # print(item)
            if item['success']:
                temp_dic = json.loads(item['result'])
                stored_handles.append(temp_dic['handle'])
            # print(stored_handles)
        for username in query_list:
            if username in stored_handles:
                for item in read_data:
                    if item['success']:
                        temp_dic = json.loads(item['result'])
                        if temp_dic['handle'] == username:
                            data.append(item)
                            break
            else:
                result = get_user_info(username)
                data.append(result)
        write_data_to_file(data, USER_INFO_SAVE)
    return data

def get_rating_data(username):
    result = []
    # 首先检查文件是否存在
    if not os.path.exists(USER_RATING_SAVE):
        # 文件不存在，进行爬取和写入操作
        result = get_user_rating(username)
        # 若无rating数据，接口返回的是字典类型，只有当存在rating数据时才进行持久化
        if isinstance(result, list):
            write_data_to_file(result, USER_RATING_SAVE)
    else:
        # 首先从文件中读取数据
        read_data = read_data_from_file(USER_RATING_SAVE)
        stored_handles = []
        for item in read_data:
            if item['handle'] in stored_handles: continue
            stored_handles.append(item['handle'])
        # print(stored_handles)
        if username in stored_handles:
            for item in read_data:
                if item['handle'] == username:
                    result.append(item)
        else:
            result = get_user_rating(username)
            # 若无rating数据，接口返回的是字典类型，只有当存在rating数据时才进行持久化
            if isinstance(result, list):
                write_data_to_file(result, USER_RATING_SAVE)
    return result

@app.route('/batchGetUserInfo', methods=['GET'])
def batchGetUserInfo():
    try:
        usernames = request.args.get('handles')
        query_list = usernames.split(',')
        data = get_info_data(query_list)
    except Exception as e:
        return '传个参数先啦'
    return jsonify(data)

@app.route('/getUserRatings', methods=['GET'])
def getUserRatings():
    try:
        username = request.args.get('handle')
        result = get_rating_data(username)
        # print(result)
        return result
    except Exception as e:
        return '传个参数先啦'



if __name__ == '__main__':
    app.run('127.0.0.1', port=2333)  # 指定提供服务的端口号
