import json
import requests
from flask import Flask, jsonify, Response
from flask import render_template  # 渲染
from flask import request

app = Flask(__name__)

url = 'https://codeforces.com/api/user.info?handles='
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/57.36'
}

@app.route('/')
def query():
  # get方法和post方法获取前端数据的方式不同
  handles = request.args.get("handles")
  name_list = str(handles).split(",")
  res_list = solve(name_list)
  # 接收结果list
  return Response(json.dumps(res_list), mimetype='application/json')

def solve(name_list):
  res_list = []
  for it in range(len(name_list)):
    try:
      user_dict = dict()
      result_dict = dict()
      response = requests.get(url=url + name_list[it], headers=headers)
      # # 情况1此handle可以查询到
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
          if not rep_info.get("rank", -1) == -1:
            result_dict["rank"] = str(rep_info["rank"]).strip()
          user_dict["result"] = result_dict
          res_list.append(user_dict)
        # 情况2此handle无法查到 返回400
      elif response.status_code == 400:
        user_dict["success"] = False
        user_dict["type"] = 1
        user_dict["message"] = "no such handle"
        res_list.append(user_dict)
        # 情况3 在查询此项时遭遇异常 HTTP 响应
      else:
        user_dict["success"] = False
        user_dict["type"] = 2
        user_dict["message"] = "HTTP response with code " + str(response.status_code)
        details = {
          "status": response.status_code
        }
        user_dict["details"] = details
        res_list.append(user_dict)
    except Exception as e:
      #情况4 ：在查询此项时未收到有效 HTTP 响应
      if isinstance(e, requests.exceptions.ConnectionError):
        user_dict = {
          "success": False,
          "type": 3,
          "message": "Request failed"
        }
      else:
        #情况5 在查询此项时程序发生运行时异常
        user_dict = {
          "success": False,
          "type": 4,
          "message": 'Internal Server Error'
        }
      res_list.append(user_dict)
  return res_list

# 自定义 500 错误处理装饰器，返回自己封装的JSON响应
if __name__ == '__main__':
  app.run(host='127.0.0.1', debug=True, port=2333)
