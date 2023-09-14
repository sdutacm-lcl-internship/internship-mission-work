import sys
import json
import requests
from lxml import html


nickname = input("please input one nickname:") 
url = "https://codeforces.com/profile/" + nickname
response = requests.get(url) 

if response.status_code == 200 :
    try:
        content = html.fromstring(response.content)
        rating = content.xpath('//div[@class="info"]/ul/li[1]/span/text()')
        rank = content.xpath('//div[@class="user-rank"]/span/text()')

        if rank[0] == "Unrated " :

            people = {
                "handle" : nickname
            }

            output = json.dumps(people) 
            print(output)
            sys.exit(0)
        elif rating and rank :

            people = {
                "handle": nickname ,"rating": rating[0],"rank": rank[0]
            }

            output = json.dumps(people)
            print(output)
            sys.exit(0)
        else:
            print("no such handle", file=sys.stderr)
            sys.exit(1)
    except IndexError:
        print("no such handle", file=sys.stderr)
        sys.exit(1)