import sys
import json
import requests

def grep_rank(handle):
    url = 'https://codeforces.com/api/user.info'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 Edg/113.0.1774.42'
    }

    param = {
        "handles": handle
    }

    response = requests.get(url = url, headers = headers, params = param)
    page = response.json()
    response_status = page['status']

    if response_status == 'OK': #请求正常
        user_info = page['result'][0]
        if 'rating' in user_info:
            ans = {
                'handle': user_info['handle'],
                'rating': user_info['rating'],
                'rank': user_info['rank']
            }
        else:
            ans = {
                'handle': user_info['handle']
            }
        ans_json = json.dumps(ans)
        sys.stdout.write(ans_json + '\n')

    elif response_status == 'FAILED': #未查找到用户
        sys.stdout.write('no such handle')
        exit(1)
    elif response_status == 'Call limit exceeded': #请求发送过快
        sys.stdout.write('请求发送频繁，请稍候！')
    elif response.status_code == 400:  #前端提交的字段名称或者字段类型和后台的实体类不一样，或者前端提交的参数跟后台需要的参数个数不一致，导致无法封装
        sys.stdout.write('请求错误！')
    elif response.status_code == 500:  #参数传入正常，服务器内部处理错误
        sys.stdout.write('服务器错误！')


def main():
    handles = sys.argv[1:]
    for handle in handles:
        grep_rank(handle)

if __name__ == "__main__":
    main()
