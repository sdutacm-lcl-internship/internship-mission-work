import datetime

import pytz
from flask import Flask, request, jsonify
from flask_caching import Cache
from utils import Crawler, Utils
from dao import Dao
from bean import UserInfo,UserRating
app = Flask(__name__)
# 两个缓存器 1放
cache_user_info = Cache(app, config={'CACHE_TYPE': 'simple'})
cache_user_ratings = Cache(app, config={'CACHE_TYPE': 'simple'})
crawler = Crawler()
myUtils = Utils()
dao = Dao

class Service:
  def __init__(self):
    pass

  def get_user_ratings(self, handle):
    try:
      #缓存中有数据，直接返回
      if not cache_user_ratings.get(handle) is None:
        return cache_user_ratings.get(handle)

      #查询数据库中是否有数据,返回一个结果列表
      ls=dao.query_ratings(handle)
      if len(ls)!=0:
        #返回结果不为空，存入缓存
        cache_user_ratings.set(handle,ls,timeout=30)
        return ls

      # 缓存和数据库中均中没有数据，30s已过。再次爬取数据并保存在数据库与缓存中
      request_results = crawler.crawl("https://codeforces.com/api/user.rating?handle={}".format(handle))

      # 2.请求后返回码为400
      if request_results['status'] == 400:
        error_message = {"message": "no such handle"}
        return error_message, 404

      # 3.请求后返回码不是400也不是200
      if request_results['status'] != 200:
        error_message = {
          "message": "An exception HTTP interface response was encountered:{}".format(request_results['status'])
        }
        return error_message, 502

      # 4.剩下的就是200，取出result。并定义一个搜集结果的列表
      result = request_results['result']
      response_data = []


      # 循环每场比赛信息
      for item in result:
        #引入对象实例user_rating
        user_rating=UserRating
        # handle可以查询到
        if "handle" in item.keys():
          user_rating.set_handle(item["handle"])
        if "contestId" in item.keys():
          user_rating.set_user_rating_id(item['contestId'])
        if "contestName" in item.keys():
          user_rating.set_contest_name(item["contestName"])
        if "rank" in item.keys():
          user_rating.set_rank(int(item["rank"]))
        if "ratingUpdateTimeSeconds" in item.keys():
          # 指定了时区
          dt_object = datetime.fromtimestamp(item["ratingUpdateTimeSeconds"], pytz.timezone('Asia/Shanghai'))
          iso_datetime_str = dt_object.isoformat()
          user_rating.set_updated_at(iso_datetime_str)
        if "oldRating" in item.keys():
          user_rating.set_old_rating(int(item["oldRating"]))
        if "newRating" in item.keys():
          user_rating.set_new_rating(int(item["newRating"]))
        response_data.append(user_rating)
      # 循环结束后将结果列表存入缓存和数据库
      cache_user_ratings.set(handle, response_data, timeout=30)
      # myUtils.data_save('data-user-ratings.txt', {"handle": handle, "info": response_data})
      # 改为存到数据库


        dao.save_ratings()

      return jsonify(response_data)
    except Exception:
      raise
      # 异常交由上层调用函数处理

  def batch_get_user_info(handles):
    request_results = {}
    response_data = []
    for name in handles:
      try:
        # 如果缓存中有该用户，则直接装进结果列表，不再请求并跳过这次循环
        if not cache_user_info.get(name) is None:
          request_results = cache_user_info.get(name)
          response_data.append(request_results)
          continue

        # 发起请求,并准备一个空的字典
        request_info = crawler.crawl('https://codeforces.com/api/user.info?handles={}'.format(name))
        # 不能用clear()此时该变量还在指向response_data中的数据
        request_results = {}

        # 返回值为400的情况
        if request_info['status'] == 400:
          request_results['success'] = False
          request_results['type'] = 1
          request_results['message'] = 'no such handle'
          response_data.append(request_results)
          continue

        # 返回值不等于400并且不等于200
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

        # 剩下的就是返回值为200的情况
        result = request_info['result'][0]
        # 有rating的情况
        if 'rating' in result:
          request_results = {

            "success": True,
            "result": {
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
        cache_user_info.set(name, request_results, timeout=30)
        # 存入文件
        myUtils.data_save('data-user-info.txt', {"handle": name, "info": request_results})


