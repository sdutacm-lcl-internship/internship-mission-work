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
            return {
                'success': False,
                'type': '1;',
                'message': "no such handle;",
            }
    except requests.exceptions.HTTPError as http_error:
        if response.status_code == 400:
            return{
                'success': False,
                'type': '1;',
                'message': "no such handle;",
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
    except requests.exceptions.RequestException as req_err:
        return {
            'success': False,
            'type': '3;',
            'message': "Request timeout"
        }
    except RuntimeError as runtime_err:
        return {
            'success': False,
            'type': '4;',
            'message': "'Internal Server Error';",
        }

def extract_user_info(user_info):
    user = {
        'success': True,
        'result': {}
    }
    if 'rank' in user_info:
        user['result']['handle'] = user_info['handle'] + ';'
        user['result']['rating'] = str(user_info['rating']) + ';'
        user['result']['rank'] = user_info['rank'] + ';'
    else:
        user['result']['handle'] = user_info['handle'] + ';'
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

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        user_info = main(name)
        return render_template('index.html', data=user_info)
    elif request.method == 'GET':
        name = request.args.get('handles', '')
        if name:
            user_info = main(name)
            return render_template('index.html', data=user_info)
        else:
            return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=2333)
