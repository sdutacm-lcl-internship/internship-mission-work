import requests
import json
import sys
from lxml import etree
def get_user_info(username):
    #链接构造
    url ='https://codeforces.com/profile/{}/'.format(username)
    #伪装header
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }
    res = requests.get(url,headers)
    if res.status_code == 200:
        f = 0
        text = res.content.decode('utf-8')
        html = etree.HTML(text)
        try:
            rank = html.xpath("//div[@class='user-rank']/span[@class='user-legendary']/text()")[0]
        except Exception as e:
            sys.stderr.write("No such handle")
            sys.exit(1)

        try:
            rating = html.xpath("//div[@class='info']/ul[1]/li[1]/span[1]/text()")[0]
        except Exception as e:
            #标记无rating记录
            f = 1
        if(f == 1):
            user_info = {
                "handle":username
            }
        else:
            user_info ={
                "handle":username,
                "rating":rating,
                "rank":rank[:-1] #去除最后一位空格
            }
        res_json = json.dumps(user_info)
        sys.stdout.write(res_json)
        sys.exit(0)
    else:
        sys.stderr.write("network anomaly")

if __name__ == '__main__':
    username = sys.argv[1:][0]
    # username = input()
    get_user_info(username)