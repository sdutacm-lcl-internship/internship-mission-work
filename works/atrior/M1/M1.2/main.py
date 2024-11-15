import requests
import json

API_URL = 'https://codeforces.com/api/user.info'
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"

def get_user_info(username, proxy=None):
    headers = {
        "User-Agent": USER_AGENT,
    }
    params = {'handles': username}

    proxies = {'http': proxy, 'https': proxy} if proxy else None
    
    try:
        response = requests.get(API_URL, headers=headers, params=params, proxies=proxies)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'OK':
            return extract_user_info(data['result'][0])
        else:
            print('No such handle')
            return None
    except requests.exceptions.RequestException as e:
        print("no such handle")
        return None

def extract_user_info(user_info):
    user={}
    if 'rank' in user_info:
        user['handle']=user_info['handle']
        user['rating']=user_info['rating']
        user['rank']=user_info['rank']
    else:
        user['handle']=user_info['handle']
    return user

def main():
    username = input()
    proxy = 'http://127.0.0.1:7890'
    user_info = get_user_info(username, proxy)
    
    if user_info:
        print(json.dumps(user_info, indent=4))

if __name__ == '__main__':
    main()