import requests
import json
import sys
from flask import Flask, render_template, request

API_URL = 'https://codeforces.com/api/user.info'
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
PROXY = 'http://127.0.0.1:7890'

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
            return "No such handle"
    except requests.exceptions.RequestException as e:
        return "no such handle"

def extract_user_info(user_info):
    user={}
    if 'rank' in user_info:
        user['handle']=user_info['handle']
        user['rating']=user_info['rating']
        user['rank']=user_info['rank']
    else:
        user['handle']=user_info['handle']
    return user

def get_user_list(usernames):
    user_list = []
    for username in usernames:
        user_list.append(get_user_info(username, PROXY))
    return user_list

def main(name):
    usernames = name.split(',')

    user_info = get_user_list(usernames)
    
    return user_info

app=Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method=='POST':
        name=request.form.get('name')
        userinfor=main(name)
        return render_template('index.html', data=userinfor)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run()