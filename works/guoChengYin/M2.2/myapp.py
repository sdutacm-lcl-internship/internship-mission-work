import json

import pytz
import requests
from datetime import datetime, timezone
from flask import Flask, Response, request, jsonify

app = Flask(__name__)


# 对于其他不可预知的错误，用一个全局异常处理器处理
@app.errorhandler(Exception)
def server_error(e):
  error_message = {"message": 'Internal Server Error'}
  return jsonify(error_message), 500


headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/57.36'
}
ratingsUrl = 'https://codeforces.com/api/user.rating?handle='


@app.route('/getUserRatings')
def get_user_ratings():
  try:
    handle = request.args.get('handle')
    handle = handle.replace('{', '').replace('}', '')
    api_res = None
    api_res = requests.get(ratingsUrl + handle, headers)
    status_code = api_res.status_code
    # handle可以查询到 200
    if status_code == 200:
      api_json = json.loads(api_res.text)
      api_result = api_json['result']
      resList = []
      for item in api_result:
        context_info = dict()
        # handle可以查询到
        if "handle" in item.keys():
          context_info['handle'] = item["handle"]
        if "contestId" in item.keys():
          context_info["contestId"] = int(item["contestId"])
        if "contestName" in item.keys():
          context_info["contestName"] = item["contestName"]
        if "rank" in item.keys():
          context_info["rank"] = int(item["rank"])
        if "ratingUpdateTimeSeconds" in item.keys():
          dt_object = datetime.fromtimestamp(item["ratingUpdateTimeSeconds"],pytz.timezone('Asia/Shanghai'))
          iso_datetime_str = dt_object.isoformat()
          # 设置时区参数
          context_info["ratingUpdatedAt"] = iso_datetime_str
        if "oldRating" in item.keys():
          context_info["oldRating"] = int(item["oldRating"])
        if "newRating" in item.keys():
          context_info["newRating"] = int(item["newRating"])
        resList.append(context_info)
      return jsonify(resList)
    # 查询不到 400 返回404
    elif status_code == 400:
      error_message = {"message": "no such handle"}
      return jsonify(error_message), 404
    # 其他返回码
    else:
      error_message = {
        "message": "An exception HTTP interface response was encountered:" + str(status_code)
      }
      return jsonify(error_message), status_code
  except Exception as e:
    # HTTP请求为未收到有效 HTTP 响应
    if api_res is None or isinstance(e, requests.exceptions.ConnectionError):
      error_message = {"message": "The HTTP interface is not responding"}
      return jsonify(error_message), 502
    # 剩下的就是服务器程序运行异常
    else:
      error_message = {"message": "Internal Server Error"}
      return jsonify(error_message), 500


userInfoUrl = 'https://codeforces.com/api/user.info?handles='


@app.route('/batchGetUserInfo')
def get_userinfo():
  handles = request.args.get('handles').replace('{', '').replace('}', '')
  names = handles.split(',')
  res = []
  for it in range(len(names)):
    try:
      user_info = dict()
      result_info = dict()
      response = None
      response = requests.get(url=userInfoUrl + names[it], headers=headers)
      # # 情况1此handle可以查询到
      if response.status_code == 200:
        rep_json = json.loads(response.text)
        # 若爬取数据status显示为”OK",赋值为True
        if rep_json["status"] == "OK":
          user_info["success"] = True
          rep_info = rep_json["result"][0]
        if not rep_info.get("handle", -1) == -1:
          result_info["handle"] = str(rep_info["handle"])
          if not rep_info.get("rating", -1) == -1:
            result_info["rating"] = int(rep_info["rating"])
          if not rep_info.get("rank", -1) == -1:
            result_info["rank"] = str(rep_info["rank"]).strip()
          user_info["result"] = result_info
          res.append(user_info)
        # 情况2此handle无法查到 400
      elif response.status_code == 400:
        error_messsage={
          "success":False,
          "type":1,
          "message":"no such handle"
        }
        res.append(error_messsage)
        # 情况3 在查询此项时遭遇异常 HTTP 响应
      else:

        details = {
          "status": response.status_code
        }
        error_messsage={
          "success":False,
          "type":2,
          "message":"An exception HTTP interface response was encountered:" + str(response.status_code),
          "details":{
          "status": response.status_code
        }
        }
        res.append(error_messsage)
    except Exception as e:
      # 情况4 ：在查询此项时未收到有效 HTTP 响应
      if isinstance(e, requests.exceptions.ConnectionError) or response is None:
        error_messsage = {"success": False, "type": 3, "message": "The HTTP interface is not responding"}
        res.append(error_messsage)
      else:
        # 情况5：剩下的就是服务器异常
        error_messsage = {
          "success": False, "type": 4, "message": 'Internal Server Error'}
      res.append(error_messsage)
  return jsonify(res), 200


if __name__ == '__main__':
  app.run(host='127.0.0.1', debug=True, port=2333)
