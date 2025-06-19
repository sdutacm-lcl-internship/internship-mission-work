import sys
import requests
import json


def solve(username):
    url = 'https://codeforces.com/api/user.info'

    params = {
        'handles': username
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:  # 检查响应状态码
        data = response.json()  # 将响应数据解析为 JSON 格式
        if data['status'] == 'OK':  # 检查 API 返回的状态
            result = data['result'][0]


            if 'rating' in result:

                output_data = {
                    "handle": username,
                    "rating": result['rating'],
                    "rank": result['rank'],
                }
            else:

                output_data = {
                    "handle": username
                }

            data_json = json.dumps(output_data)
            sys.stdout.write(data_json + "\n")
            sys.exit(0)
    else:
            sys.stderr.write("no such handle\n")
            sys.exit(1)



def main():


    username = sys.argv[1]
    solve(username)


if __name__ == '__main__':
    main()