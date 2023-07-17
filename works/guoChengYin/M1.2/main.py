import json
import sys
import requests


def solve(usernames):
  #拼接字符串,并以;分割
  usernames = ';'.join(usernames)

  url = 'https://codeforces.com/api/user.info?handles='+usernames
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/57.36'
  }
  response=requests.get(url=url,headers=headers)
  status_code = response.status_code
  if status_code==200:
    # 使用json的loads方法将字符串对象转化为pyhon对象
    res = json.loads(response.text)
    # 结果列表user_list
    user_list = res['result']

    # 从结果列表中取出数据并封装
    data = []
    for item in user_list:
      user_dic=dict()
      user_dic["handle"]=str(item['handle']).strip()
      #使用dict.get(key,defaultValue)方法，避免出现keyError
      if not item.get("rating",-1)==-1:
       user_dic["rating"]=int(item['rating'])
      if not item.get("rank",-1)==-1:
       user_dic["rank"] = str(item['rank']).strip()
      data.append(user_dic)
    json_data=json.dumps(data)
    sys.stdout.write(json_data+"\n")
    return 0
  #异常情况1 400，”不存在的域名“ 认为没有该选手的信息
  elif status_code==400:
    sys.stderr.write('no such handle' + "\n"+'ErrorCode '+str(status_code)+"\n")
    return 1
  #异常情况2 访问被拒绝403
  elif status_code==403:
    sys.stderr.write('request was denied'+"\n"+"ErrorCode"+str(status_code)+"\n")
    return 1
  #其他异常码
  else:
    sys.stderr.write('other errors' + "\n" + "ErrorCode" + str(status_code) + "\n")
    return 1


if __name__ == '__main__':

  args=sys.argv[1:]
  #异常情况3  防止空输入
  if len(args)==0:
    returnCode=1
    sys.stderr.write("The input cannot be empty"+"\n")
  else:
    returnCode=solve(args)
  exit(returnCode)


