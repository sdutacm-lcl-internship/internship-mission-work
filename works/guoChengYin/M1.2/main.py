import json
import sys
import requests


def solve(username):
  #单个用户
  url = 'https://codeforces.com/api/user.info?handles='+username
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/57.36'
  }
  response=requests.get(url=url,headers=headers)
  status_code = response.status_code
  if status_code==200:
    # 使用json的loads方法将字符串对象转化为pyhon对象
    res_py = json.loads(response.text)
    # 用户数据user_data
    user_data = res_py['result'][0]

    #创建空字典用来保存提取的用户数据
    user_dic = dict()
    #返回码为200，handle存在,不用担心keyError
    user_dic["handle"]=str(user_data["handle"]).strip()
    #对于rating为空的情况，user_dict不会添加rating信息，保证了数据格式正确
    if not user_data.get("rating",-1)==-1:
      user_dic["rating"]=int(user_data["rating"])
    if not user_data.get("rank",-1)==-1:
      user_dic["rank"]=str(user_data["rank"]).strip()

    #封装
    json_data=json.dumps(user_data)
    sys.stdout.write(json_data+"\n")
  elif status_code==400:
    sys.stderr.write('您要寻找的用户不存在\n错误代码'+str(status_code)+"\n")
    return 1
  elif status_code==403:
    sys.stderr.write("您的请求被拒绝，可增加动态headers或者使用代理ip\n错误代码"+str(status_code)+"\n")
    return 1
  elif status_code==404:
    sys.stderr.write("找不到资源,可重新检查url和headers\n错误代码"+str(status_code)+"\n")
  elif status_code==503:
    sys.stderr.write("服务器过载,可调用time.sleep(s)或减少线程数目降低爬取频率\n错误代码"+str(status_code)+"\n")
  else:
    sys.stderr.write("其他错误类型\n错误代码"+str(status_code)+"\n")


if __name__ == '__main__':
  args=sys.argv[1:]
  return_code=0
  #异常情况3  防止空输入
  if len(args)==0:
    return_code=1
    sys.stderr.write("The input cannot be empty"+"\n")
  else:
    for username in args:
      return_code=solve(username)
      #如果发现错误信息，立即退出程序
      if return_code==1:
        exit(return_code)
  #正常退出程序
  exit(return_code)


