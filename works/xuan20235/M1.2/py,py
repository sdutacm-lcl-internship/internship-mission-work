from http.client import responses
import requests
import json
import os
import re
from bs4 import BeautifulSoup
import lxml
import sys
import time


#import chaojiying
def func(handle):
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    methodName = "user.info"
    url_base = f"https://codeforces.com/api/{methodName}"

    pa = {"handles": handle}
    response = requests.get(url=url_base, params=pa, headers=headers)
    #print(response.status_code)
    if response.status_code != 200 and response.status_code != 400:  #1 解决url 错误 400是没找到通过下面的来处理
        sys.stderr.write(f"status_code ={response.status_code}\n")
        return 2
    load_json = json.loads(response.text)
    #print(load_json)
    if load_json["status"] == 'FAILED':
        sys.stderr.write("no such handle\n")
        #print(1)
        return 1
    else:

        load_json = json.loads(response.text)

        result = load_json["result"]

        try:
            rate = result[0]["rating"]
            rank = ""
            for tmp in result[0]["rank"]:
                rank = rank + tmp

            ans = {"handle": handle, "rate": rate, "rank": rank.strip()}
            res_json = json.dumps(ans)
            sys.stdout.write(res_json + '\n')
        except:
            ans = {"handle": handle}
            res_json = json.dumps(ans)
            sys.stdout.write(res_json + '\n')


def main():

    args = sys.argv[1:]
    for arg in args:
        f = 1
        exit_f = 0
        for i in range(1, 10):  # 2解决网络不佳 自动重连
            try:
                if func(arg) == 1:
                    exit_f = 1
                    f = 0
                    break
                f = 0
                break
            except:
                continue
            time.sleep(1)  #3 防止访问太多被拉黑了
        if f == 1:
            sys.stderr.write("无法链接到网络\n")
        if exit_f == 1:
            sys.exit(1)  #无法找到用户时 exit 1


if __name__ == "__main__":
    main()#随便加点东西
