import requests
import sys
import json
def solve(name):
    url='https://codeforces.com/api/user.info?handles='+name
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    response=requests.get(url=url,headers=headers)
    status_code=response.status_code
    if status_code==200:
        date=response.json()
        for user in date["result"]:
            if "rank" not in user:
                ans={"handle":name}
            else:
                ans={"handle":name,
                     "rating":user["rating"],
                     "rank":user["rank"]}
            ans=json.dumps(ans)
            sys.stdout.write(ans+"\n")
    else:
        if status_code==400:
            sys.stderr.write("no such handle\n")
        elif status_code==403:
            sys.stderr.write("Access Forbidden: {}".format(status_code) + '\n')
        elif status_code==404:
            sys.stderr.write("Not Found: {}".format(status_code.code) + '\n')
        elif status_code==503:
            sys.stderr.write("Service Unavailable: {}".format(status_code.code) + '\n')
        else:
            sys.stderr.write("ErrorCode:{}".format(status_code) + "\n")

def main():
    sname=sys.argv[1:]
    for name in sname:
        solve(name)
    exit(1)
if __name__=='__main__':
    main()
