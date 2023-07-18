import json
from multiprocessing.dummy import Pool
import requests
from flask import Flask, jsonify
from flask import render_template  # 渲染
from flask import request
app = Flask(__name__)


@app.route('/')  # 初始化加载主页
def init():
  return render_template('index.html')


@app.route('/query',methods=["GET","POST"])
def query():
  #get方法和post方法获取前端数据的方式不同
  val=request.args.get("val")
  name_list = str(val).split(",")
  #接收序列化结果
  res_list=solve(name_list)
  return jsonify(res_list)

def solve(name_list):
  url = 'https://codeforces.com/api/user.info?handles='
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/57.36'
  }

  #结果收集列表
  res_list=[]
  # 逐个姓名查询，避免由于单个用户异常导致所有查询失败
  for user_name in name_list:
    user_dict = dict()
    result_dict = dict()
    response = requests.get(url=url + user_name, headers=headers)
    # 情况1此handle可以查询到
    if response.status_code == 200:
      rep_json = json.loads(response.text)
      # 若爬取数据status显示为”OK",赋值为True
      if rep_json["status"] == "OK":
        user_dict["success"] = True
        rep_info = rep_json["result"][0]
      if not rep_info.get("handle", -1) == -1:
        result_dict["handle"] = str(rep_info["handle"])
        if not rep_info.get("rating", -1) == -1:
          result_dict["rating"] = int(rep_info["rating"])
        if not user_dict.get("rank", -1) == -1:
          result_dict["rank"] = str(rep_info["rank"]).strip()
        user_dict["result"] = result_dict
        res_list.append(user_dict)
      # 情况2此handle无法查到
    elif response.status_code==400:
        user_dict["success"] = False
        user_dict["type"] = 1
        user_dict["message"] = "no such handle"
        res_list.append(user_dict)
    else:
      user_dict["success"] = False
      user_dict["type"] = 2
      user_dict["message"] = "NetworkError"
      details = {
        "status": response.status_code
      }
      user_dict["details"] = details
      res_list.append(user_dict)
  return str(res_list)


if __name__ == '__main__':
  app.run(host='127.0.0.1', debug=True, port=2333)
