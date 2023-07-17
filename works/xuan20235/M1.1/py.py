import requests
import json
import os
import re
from bs4 import BeautifulSoup
import lxml
import sys
#import chaojiying

headers={
 "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
url_base="https://codeforces.com/profile/"
#handle=input("输入要查询的用户名")
#handle="aaabbbbccc00"
args=sys.argv[1:]
for arg in args :
    handle=arg
    url=url_base+handle
    response=requests.get(url=url,headers=headers)
    #print(response.status_code)
    if response.status_code==200 :
        page_text=response.text
        #print(page_text)
        soup=BeautifulSoup(page_text,"lxml")
        a=soup.select(".info > ul > li >span")
        if len(a)!=0:
            rate=a[0].string
            
            if rate!="0":
                b=soup.select(".info > div > div > span")
                rank=b[0].string
                date={
                "handle": handle,
                "rating": rate,
                "rank": rank.strip()}
                res_json=json.dumps(date)
                sys.stdout.write(res_json + '\n')
            else :
                date={
                    "handle":handle
                }
                res_json=json.dumps(date)
                sys.stdout.write(res_json + '\n')
        else :
            sys.stderr.write("no such handle\n")
            sys.exit(1) 
print("over!")
