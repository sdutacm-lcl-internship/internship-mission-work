import requests
import json
import sys


def solve(username):
    url = "https://codeforces.com/api/user.info"
    # 请求的handles参数
    params = {
        "handles": username
    }
    try:
        response = requests.get(url, params=params)
        # 第三种情况，发生了404或500错误
        if response.status_code == 500:
            sys.stderr.write("Program encountered an exception and terminated prematurely\n")
            sys.exit(1)
        elif response.status_code == 404:
            sys.stderr.write("Not found\n")
            sys.exit(1)
        #访问频率过快时会出现503错误
        elif response.status_code == 503:
            sys.stderr.write("Access frequency too fast\n")
            sys.exit(1)
        data = response.json()
        if data["status"] == "OK":
            for user in data["result"]:
                # 查看rank这个键是否存在，若不存在那么就是没用rating的用户
                if "rank" not in user:
                    user_info = {"handle": params["handles"]}
                else:
                    user_info = {
                        "handle": params["handles"],
                        "rating": user["rating"],
                        "rank": user["rank"]
                    }
                user_json = json.dumps(user_info)
                sys.stdout.write(user_json + "\n")
        # 因为前面把错误的状态码都筛选掉了，所以剩下的就是查无此人的情况了
        elif data["status"] == "FAILED":
            sys.stderr.write("no such handle\n")
            sys.exit(1)
    # 第一种情况，我断网了，无法访问api
    except requests.exceptions.RequestException as e:
        sys.stderr.write("无法访问api，请尝试检查网络\n")
        sys.exit(1)


def main():
    try:
        username = sys.argv[1:][0]
        solve(username)
    # 第二种情况：只输入了空格，或者没有输入，这种情况下会出现索引越界的情况
    except IndexError:
        sys.stderr.write("不能只输入空格或不输入！\n")


if __name__ == '__main__':
    main()
