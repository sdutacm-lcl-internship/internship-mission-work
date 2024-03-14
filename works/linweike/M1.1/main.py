from bs4 import BeautifulSoup
import requests
import json
import re
import sys
def solve(name):
    headers = {
        'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36 Edg/122.0.0.0'
    }
    response = requests.get("https://codeforces.com/profile/{}/".format(name),headers=headers)
    if response.status_code == 200:
        html = response.text
        #筛选标志量，判断是否成功跳转到用户界面
        flage = re.compile(r'<div class="user-rank">(.*?)</div>', re.S)
        findrank = re.compile(r'<span class="user-.*?">(.*?) </span>',re.S)
        findrating = re.compile(r'<span style="font-weight:bold;" class="user-.*?">(.*?)</span>',re.S)
        #筛选真实姓名而不是用户查找时不区分大小写的姓名
        findname = re.compile(r'<a href="/profile/(.*?) title=".*?" class=".*?-user user-.*?">',re.S)
        #标志量
        flage_list = re.findall(flage, html)
        if len(flage_list) == 0:
            sys.stdout.write("Can't find such user\n")
        else:
            rank = re.findall(findrank, html)
            rating = re.findall(findrating, html)
            truename=re.findall(findname,html)
            for str in truename:
                str=str[:-1]
                str_ori = str
                if str.lower() == name:
                    name = str_ori
            if (len(rank) == 0 or len(rating) == 0):
                ans = {
                    'handle' : name,
                }
            else :
                ans = {
                    'handle' : name,
                    'rating' : rating[0],
                    'rank' : rank[0],
                }
            ans = json.dumps(ans)
            #print(ans)
            sys.stdout.write(ans + '\n')

def main():
    names = sys.argv[1:]
    for name in names:
        solve(name)

if __name__ == '__main__':
    main()