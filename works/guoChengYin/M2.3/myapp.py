from datetime import datetime, timezone

import pytz
import requests
from flask import Flask, request, jsonify
from flask_caching import Cache

from utils.my_utils import Crawler

app = Flask(__name__)
#两个缓存器
cache_1 = Cache(app, config={'CACHE_TYPE': 'simple'})
cache_2 = Cache(app, config={'CACHE_TYPE': 'simple'})
#自定义爬虫
crawler = Crawler()
# 对于其他不可预知的错误，用一个全局异常处理器处理
@app.errorhandler(Exception)
def server_error(e):
  return jsonify(str(e))


# 路由1 选手信息
@app.route('/batchGetUserInfo')
def batch_get_user_info():
  handles = request.args.get('handles', '')
  names = handles.replace('{', '').replace('}', '').split(',')
  request_results = {}
  response_data = []
  for name in names:
    try:
      # 如果缓存中有该用户，则直接装进结果列表，不再请求
      if not cache_1.get(name) is None:
        request_results = cache_1.get(name)
      #缓存中无该用户，再次请求
      else:
        request_info = crawler.crawl('https://codeforces.com/api/user.info?handles=' + name)
        if request_info['status'] == 200:
          result = request_info['result'][0]
          # 有rating的情况
          if 'rating' in result:
            request_results['success'] = True
            request_results['result'] = {
              "handle": result['handle'],
              "rating": int(result['rating']),
              "rank": result['rank']
            }
          else:
            # 无rating的情况
            request_results['success'] = True
            request_results['result'] = {
              "handle": result['handle']
            }
          #缓存中只保存正常返回200的数据，不保留其他
          cache_1.set(name, request_results, timeout=15)
        else:
          # 未返回200，返回400
          if request_info['status'] == 400:
            request_results['success'] = False
            request_results['type'] = 1
            request_results['message'] = 'no such handle'
          else:
            # 返回其他状态码
            request_results['success'] = False
            request_results['type'] = 2
            request_results['message'] = 'An exception HTTP interface response was encountered: ' + request_info['status']
            request_results['details'] = {
              "status": request_info['status']
            }
      #处理异常
    except Exception as e:
      #第一种异常，请求异常，未收到有效响应
      if isinstance(e, requests.exceptions.ConnectionError):
        request_results['success'] = False
        request_results['type'] = 3
        request_results['message'] = 'The HTTP interface is not responding'
      else:
        #剩下的其他异常认为是服务器异常
        request_results['success'] = False
        request_results['type'] = 4
        request_results['message'] = 'Internal Server Error'
    #该次循环的name的所有情况判断完毕(包括异常情况），装进结果列表
    response_data.append(request_results)
    # 重置一下
    request_results = {}

  return jsonify(response_data), 200

@app.route('/getUserRatings')
def get_user_ratings():
  try:
    handle = request.args.get('handle')
    handle = handle.replace('{', '').replace('}', '')
    if not cache_2.get(handle) is None:
      return jsonify(cache_2.get(handle))
    request_results=crawler.crawl("https://codeforces.com/api/user.rating?handle={}".format(handle))
    # handle可以查询到 200
    if request_results['status'] == 200:
      result = request_results['result']
      response_data = []
      for item in result:
        #循环每一场比赛的信息
        context_info = {}
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
          #指定了时区
          dt_object = datetime.fromtimestamp(item["ratingUpdateTimeSeconds"],pytz.timezone('Asia/Shanghai'))
          iso_datetime_str = dt_object.isoformat()
          context_info["ratingUpdatedAt"] = iso_datetime_str
        if "oldRating" in item.keys():
          context_info["oldRating"] = int(item["oldRating"])
        if "newRating" in item.keys():
          context_info["newRating"] = int(item["newRating"])
        response_data.append(context_info)
      #只缓存200的信息
      cache_2.set(handle, response_data, timeout=15)
      return jsonify(response_data)
        # 查询不到 400 返回404
    elif request_results['status'] == 400:
      error_message = {"message": "no such handle"}
      return jsonify(error_message), 404
      # 其他返回码
    else:
      error_message = {
        "message": "An exception HTTP interface response was encountered:" + str(request_results['status'])
      }
      return jsonify(error_message), request_results['status']
  except Exception as e:
      # HTTP请求为未收到有效 HTTP 响应
      if request_results is None or isinstance(e, requests.exceptions.ConnectionError):
        error_message = {"message": "The HTTP interface is not responding"}
        return jsonify(error_message), 502
      # 剩下的就是服务器程序运行异常
      else:
        raise

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=2333)
