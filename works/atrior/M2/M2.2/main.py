import requests
import json
import sys
from flask import Flask, render_template, request, current_app
import traceback
import datetime
import pytz

API_URL = 'https://codeforces.com/api/user.info'
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
PROXY = 'http://127.0.0.1:7890'
RATING_URL = 'https://codeforces.com/api/user.rating'

app = Flask(__name__)

# 获取选手 infor
def unix_to_iso(unix_time): # 将一个 Unix 时间戳（即自 1970年1月1日起的秒数）转换为一个 ISO 8601 格式的日期时间字符串。
    Date_Time = datetime.datetime.fromtimestamp(unix_time, pytz.timezone('Asia/Shanghai'))
    Iso_Time = Date_Time.isoformat()
    return Iso_Time

def get_user_info(username, proxy):
    headers = {
        "User-Agent": USER_AGENT,
    }
    params = {'handles': username}

    proxies = {'http': proxy, 'https': proxy} if proxy else {}

    try:
        response = requests.get(API_URL, headers=headers, params=params, proxies=proxies)
        response.raise_for_status() 
        data = response.json()
        if data['status'] == 'OK':
            return extract_user_info(data['result'][0])
        else:
            return {
                'success': False,
                'type': '1',
                'message': "no such handle",
            }
    except requests.exceptions.HTTPError:
        if response.status_code == 400:
            return{
                'success': False,
                'type': '1',
                'message': "no such handle",
            }
        else:
            return {
            'success': False,
            'type': '2;',
            'message': f"HTTP response with code {response.status_code}",
            'details':{
                'status':f'{response.status_code};'
            }
        }
    except requests.exceptions.RequestException:
        return {
            'success': False,
            'type': '3;',
            'message': "Request timeout"
        }
    except RuntimeError:
        return {
            'success': False,
            'type': '4;',
            'message': "'Internal Server Error'",
        }
    except ZeroDivisionError: # 除0
        return {
            'success': False,
            'type': '4;',
            'message': "'Internal Server Error'",
        }
    except ValueError:  # 值错误（字母->整数
        return {
            'success': False,
            'type': '4;',
            'message': "'Internal Server Error'",
        }
    except TypeError: # 数据类型
        return {
            'success': False,
            'type': '4;',
            'message': "'Internal Server Error'",
        }
    except IndexError: # 超出索引
        return {
            'success': False,
            'type': '4;',
            'message': "'Internal Server Error'",
        }
    except KeyError: # 字典中没有指定的key
        return {
            'success': False,
            'type': '4;',
            'message': "'Internal Server Error'",
        }
    except FileNotFoundError: # 文件未找到
        return {
            'success': False,
            'type': '4;',
            'message': "'Internal Server Error'",
        }

def extract_user_info(user_info):
    user = {
        'success': True,
        'result': {}
    }
    if 'rank' in user_info:
        user['result']['handle'] = user_info['handle']
        user['result']['rating'] = str(user_info['rating'])
        user['result']['rank'] = user_info['rank']
    else:
        user['result']['handle'] = user_info['handle']
    return user

def get_user_list(usernames):
    user_list = []
    for username in usernames:
        user_list.append(get_user_info(username, PROXY))
    format_usr_list=[json.dumps(d, indent=4, ensure_ascii=False) for d in user_list]
    return format_usr_list

def main(name):
    usernames = name.split(',')
    user_info = get_user_list(usernames)
    return user_info

# 获取选手 rating

def extract_user_rating(userrating):
    user={
        
    }
    if 'rank' in userrating:
        user['handle']=userrating['handle']
        user['contestId']=userrating['contestId']
        user['contestName']=userrating['contestName']
        user['rank']=userrating['rank']
        user['ratingUpdateAt']=unix_to_iso(userrating['ratingUpdateTimeSeconds'])
        user['oldRating']=userrating['oldRating']
        user['newRating']=userrating['newRating']
        return user

def get_usr_rating(username):
    headers = {
        "User-Agent": USER_AGENT,
    }
    proxies = {'http': PROXY, 'https': PROXY} if PROXY else {}
    params={'handle':username}
    try:
        response = requests.get(RATING_URL, headers=headers, proxies=proxies, params=params)
        response.raise_for_status()
        rating = response.json()
        usrrating=[]
        for i in rating['result']:
            usrrating.append(extract_user_rating(i))
        return usrrating
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            return{
                'message': "no such handle",
            }
        else:
            return {
            'message': f"{e}",
        }
    except Exception as e:
        return {
            'message':f"{e}"
        }

def rating(ulist):
    if ulist == '':
        return []
    userlist=ulist.split(',')
    arr=[]
    for i in userlist:
        arr.append(get_usr_rating(i))
    format_arr=[json.dumps(d, indent=4, ensure_ascii=False) for d in arr]
    return format_arr

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/batchGetUserInfo', methods=['GET', 'POST'])
def index1():
    if request.method == 'POST':
        name = request.form.get('name')
        user_info = main(name)
        return render_template('index1.html', data=user_info)
    elif request.method == 'GET':
        name = request.args.get('handles', '')
        if name:
            user_info = main(name)
            return render_template('index1.html', data=user_info)
        else:
            return render_template('index1.html')

@app.route('/getUserRatings', methods=["GET", "POST"])
def index2():
    if request.method=='POST':
        name=request.form.get('name')
        ratings=rating(name)
        return render_template('index2.html', data=ratings)
    elif request.method == 'GET':
        name=request.args.get('handle', '')
        ratings=rating(name)
        return render_template('index2.html', data=ratings)

@app.route('/favicon.ico')
def get_fav():
    return current_app.send_static_file('icon/circular_icon.ico')

if __name__ == '__main__':
    app.run(debug=True, port=2333)