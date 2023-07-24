import json

from my_utils.utils import Utils

from datetime import datetime

import pytz
import requests
from flask import Flask, request, jsonify
from flask_caching import Cache

from my_utils.utils import Crawler

app = Flask(__name__)
#两个缓存器 1放
cache_user_info = Cache(app, config={'CACHE_TYPE': 'simple'})
cache_user_ratings = Cache(app, config={'CACHE_TYPE': 'simple'})
#自定义爬虫
crawler = Crawler()

myUtils = Utils()
# 捕捉其他不可预知的错误，用一个全局异常处理器处理
# @app.errorhandler(Exception)
# def server_error(e):
#   error_message = {"message": 'Internal Server Error'}
#   return jsonify(error_message), 500


# 路由1 选手信息
@app.route('/batchGetUserInfo')
def batch_get_user_info():
  handles = request.args.get('handles', '')
  names = handles.replace('{', '').replace('}', '').split(',')
  request_results = {}
  response_data = []
  for name in names:
    try:
      # 如果缓存中有该用户，则直接装进结果列表，不再请求并跳过这次循环
      if not cache_user_info.get(name) is None:
        request_results = cache_user_info.get(name)
        response_data.append(request_results)
        continue


      # 发起请求,并准备一个空的字典
      request_info = crawler.crawl('https://codeforces.com/api/user.info?handles={}'.format(name))
      #不能用clear()此时该变量还在指向response_data中的数据
      request_results={}


      #返回值为400的情况
      if request_info['status'] == 400:
        request_results['success'] = False
        request_results['type'] = 1
        request_results['message'] = 'no such handle'
        response_data.append(request_results)
        continue


      #返回值不等于400并且不等于200
      if request_info['status'] != 200:
        request_results['success'] = False
        request_results['type'] = 2
        request_results['message'] = 'An exception HTTP interface response was encountered: ' + request_info[
          'status']
        request_results['details'] = {
          "status": request_info['status']
        }
        response_data.append(request_results)
        continue


      #剩下的就是返回值为200的情况
      result = request_info['result'][0]
      # 有rating的情况
      if 'rating' in result:
        request_results={

          "success":True,
          "result":{
          "handle": result['handle'],
          "rating": int(result['rating']),
          "rank": result['rank']
        }
        }
      else:
        # 无rating的情况
        request_results['success'] = True
        request_results['result'] = {
          "handle": result['handle']
        }
      # 缓存中只存返回码为200的情况
      response_data.append(request_results)
      print(response_data)
      cache_user_info.set(name, request_results, timeout=30)
      #存入文件
      myUtils.data_save('data-user-info.txt', {"handle": name, "info": request_results})
    except Exception as e:
      # 第一种异常，请求异常，未收到有效响应
      if isinstance(e, requests.exceptions.ConnectionError):
        request_results['success'] = False
        request_results['type'] = 3
        request_results['message'] = 'The HTTP interface is not responding'
      else:
        # 剩下的其他异常认为是服务器异常
        request_results['success'] = False
        request_results['type'] = 4
        request_results['message'] = 'Internal Server Error'

        response_data.append(request_results)

  return jsonify(response_data), 200














#路由2 比赛信息
@app.route('/getUserRatings')
def get_user_ratings():
  try:
    handle = request.args.get('handle')
    handle = handle.replace('{', '').replace('}', '')
    # 1.缓存中有数据
    print(cache_user_ratings.get(handle))
    if not cache_user_ratings.get(handle) is None:
      return jsonify(cache_user_ratings.get(handle))

    # 缓存中没有数据，发起请求
    request_results = crawler.crawl("https://codeforces.com/api/user.rating?handle={}".format(handle))

    # 2.请求后返回码为400
    if request_results['status'] == 400:
      error_message = {"message": "no such handle"}
      return jsonify(error_message), 404

    # 3.请求后返回码不是400也不是200
    if request_results['status'] != 200:
      error_message = {
        "message": "An exception HTTP interface response was encountered:{}" .format(request_results['status'])
      }

    # 4.剩下的就是200，取出result。并定义一个搜集结果的列表
    result = request_results['result']
    response_data = []

    # 循环每场比赛信息
    for item in result:
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
        # 指定了时区
        dt_object = datetime.fromtimestamp(item["ratingUpdateTimeSeconds"], pytz.timezone('Asia/Shanghai'))
        iso_datetime_str = dt_object.isoformat()
        context_info["ratingUpdatedAt"] = iso_datetime_str
      if "oldRating" in item.keys():
        context_info["oldRating"] = int(item["oldRating"])
      if "newRating" in item.keys():
        context_info["newRating"] = int(item["newRating"])
      response_data.append(context_info)
    # 循环结束后将结果列表存入缓存和文件
    cache_user_ratings.set(handle, response_data, timeout=30)
    myUtils.data_save('data-user-ratings.txt', {"handle": handle, "info": response_data})

    return jsonify(response_data)
  except Exception as e:
    # HTTP请求为未收到有效 HTTP 响应
    if isinstance(e, requests.exceptions.ConnectionError):
      error_message = {"message": "The HTTP interface is not responding"}
      return jsonify(error_message), 502
    # 剩下的就是服务器程序运行异常,交给全局异常处理器处理
    else:
      raise




#项目启动前将txt文件中保存的数据加载到缓存中
def load_cache():
  user_info=myUtils.read_file('data-user-info.txt')
  user_ratings=myUtils.read_file('data-user-ratings.txt')
  for name in user_info.keys():
    cache_user_info.set(name, user_info[name], timeout=30)
  for name in  user_ratings.keys():
    cache_user_ratings.set(name, user_ratings[name], timeout=30)





if __name__ == '__main__':
  #项目启动前先将文件中的数据填充到缓存中
  load_cache()
  app.run(host='127.0.0.1', port=2333)
