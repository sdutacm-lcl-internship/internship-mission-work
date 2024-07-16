import requests
import json
import re
import sys
def solve(name):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    url="https://codeforces.com/profile/"+name
    response=requests.get(url=url, headers=headers) #响应
    if response.status_code==200:
        # 正则表达式
        flag=re.compile(r'<div class="user-rank">(.*?)</div>',re.S)
        findrank = re.compile(r'<span class="user-.*?">(.*?) </span>', re.S)
        findrate = re.compile(r'<span style="font-weight:bold;" class="user-.*?">(.*?)</span>', re.S)
        findname = re.compile(r'<a href="/profile/(.*?) title=".*?" class=".*?-user user-.*?">', re.S)
        html = response.text
        list=re.findall(flag,html)
        if len(list)==0:
            sys.stderr.write("no such handle\n")
            sys.exit(1)
        else:
            rank=re.findall(findrank,html)
            rate=re.findall(findrate,html)
            tname=re.findall(findname,html)
            for str in tname:
                tt=str[:-1]
                if tt.lower()==name:
                    name=tt
            if len(rank)==0 or len(rate)==0:
                ans={'handle':name,}
            else:
                ans={
                    "handle":name,
                    'rating':int(rate[0]),
                    'rank':rank[0],
                }
            ans=json.dumps(ans)
            sys.stdout.write(ans+"\n")

if  __name__=='__main__':
    names=sys.argv[1:]
    for name in names:
        solve(name)
