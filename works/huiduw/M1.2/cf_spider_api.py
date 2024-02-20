import requests
import json
import sys


def get_user_info(username):
    url = "https://codeforces.com/api/user.info"
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }
    # 配置参数
    params = {
        "handles": username
    }
    try:
        res = requests.get(url,params, headers = headers)
        info_json = res.json()
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
                sys.stdout.write(user_json + "\n")
        elif info_json["status"] == "FAILED":
            sys.stderr.write("no such handle\n")
            sys.exit(1)
    except requests.exceptions.Timeout as e:
        sys.stderr.write(f"请求超时: {e}\n")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        sys.stderr.write(f"HTTP错误: {e}\n")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        sys.stderr.write(f"连接错误: {e}\n")
        sys.exit(1)
    except KeyError as e:
        sys.stderr.write(f"API返回的数据不完整或不正确: {e}\n")
        sys.exit(1)
    except TypeError as e:
        sys.stderr.write(f"返回的数据类型不正确: {e}\n")
        sys.exit(1)

def main():
    try:
        username = sys.argv[1:][0]
        get_user_info(username)
    except IndexError:
        sys.stderr.write("用户名不能为空!\n")


if __name__ == '__main__':
    main()