from bs4 import BeautifulSoup
import requests
import json
import re
import sys
#python D:\python-test\main.py jiangly
def solve(name):
    headers = {
        'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36 Edg/122.0.0.0'
    }
    param = {
        "handles": name
    }
    try:
        response = requests.get("https://codeforces.com/api/user.info",headers=headers, params = param)
        status_code = response.status_code
        if status_code == 200:
            res_json = json.loads(response.text)
            user_data=res_json['result'][0]
            if 'rating' in user_data:
                ans = {
                    'handle':user_data['handle'],
                    'rating': int(user_data['rating']),
                    'rank':user_data['rank']
                }
            else:
                ans = {
                   'handle':user_data['handle']
                }
            json_data = json.dumps(ans)
            sys.stdout.write(json_data + '\n')
        elif status_code == 400:
            sys.stderr.write("no such handles\n")
            sys.exit(1)
        elif status_code == 404:
            sys.stderr.write("Not Found: 404\n")
            sys.exit(1)
        elif status_code == 403:
            sys.stderr.write("HTTP 403 Forbidden\n")
            sys.exit(1)
        elif status_code == 503:
            sys.stderr.write("Service Unavailable 503\n")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        sys.stderr.write("无网络链接。\n")
        sys.exit(1)
def main():
    names = sys.argv[1:]
    for name in names:
        solve(name)

if __name__ == '__main__':
    main()