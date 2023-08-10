import datetime
import sqlite3
import time
import pytz
import requests
from utils import Crawler, Utils
from user_dao import Dao

# 两个缓存器 1放


crawler = Crawler()
myUtils = Utils()
dao = Dao()


class Service:
  def __init__(self, cache_user_info, cache_user_ratings):
    self.cache_user_info = cache_user_info
    self.cache_user_ratings = cache_user_ratings

  def get_user_ratings(self, handle):
    try:
      # 缓存中有数据，直接返回
      if not self.cache_user_ratings.get(handle) is None:
        return self.cache_user_ratings.get(handle), 200

      # 查询数据库中是否有数据,返回一个结果列表
      res = dao.query_ratings(handle)
      if len(res) != 0:
        # 返回结果不为空，存入缓存
        self.cache_user_ratings.set(handle, res[0:-1], timeout=30 - res[-1])
        res = res[0:-1]
        return res, 200

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
        # 引入对象实例user_rating
        rating = {}
        # handle可以查询到
        if "handle" in item.keys():
          rating["handle"] = item["handle"]
        if "contestId" in item.keys():
          rating["contestId"] = item['contestId']
        if "contestName" in item.keys():
          rating["contestName"] = item["contestName"]
        if "rank" in item.keys():
          rating["rank"] = item["rank"]
        if "ratingUpdateTimeSeconds" in item.keys():
          # 指定了时区
          dt_object = datetime.datetime.fromtimestamp(item["ratingUpdateTimeSeconds"], pytz.timezone('Asia/Shanghai'))
          iso_datetime_str = dt_object.isoformat()
          rating["ratingUpdatedAt"] = iso_datetime_str
        if "oldRating" in item.keys():
          rating["oldRating"] = int(item["oldRating"])
        if "newRating" in item.keys():
          rating["newRating"] = int(item["newRating"])
        response_data.append(rating)
      # 循环结束后将结果列表存入缓存和数据库
      self.cache_user_ratings.set(handle, response_data, timeout=30)
      try:
        dao.save_ratings(handle, response_data, round(time.time()))
      except Exception as e:
        '''若为外键约束异常，
      则调用查询用户信息的方法将用户信息存入user_info表，
      然后再次调用保存比赛信息到数据库的方法。'''
        if isinstance(e, sqlite3.IntegrityError):
          self.batch_get_user_info([handle])
          dao.save_ratings(handle, response_data, round(time.time()))
        else:
          raise
          # 返回数据
      return response_data, 200
    except Exception as e:
      # HTTP请求为未收到有效 HTTP 响应
      if isinstance(e, requests.exceptions.ConnectionError):
        error_message = {"message": "HTTP interface not responding·"}
        return error_message, 502
      # 剩下的就是服务器程序运行异常,
      elif isinstance(e, sqlite3.OperationalError):
        error_message = {"message": "Internal Server Error"}
        return error_message, 500

  def batch_get_user_info(self, handles):
    response_data = []
    for handle in handles:
      try:
        # 如果缓存中有该用户，则直接装进结果列表，不再请求并跳过这次循环
        if not self.cache_user_info.get(handle) is None:
          request_results = self.cache_user_info.get(handle)
          response_data.append(request_results)
          continue
        # 若缓存中没有数据，查询数据库中有没有
        res = dao.query_user_info(handle)
        if len(res) != 0:
          if res[1] == 0:
            request_results = {
              "success": True,
              "result": {
                "handle": res[0]
              }
            }
          else:
            # 返回结果不为空，存入缓存，返回结果
            request_results = {
              "success": True,
              "result": {
                "handle": res[0],
                "rating": res[1],
                "rank": res[2]
              }
            }
          self.cache_user_info.set(handle, request_results, timeout=30 - res[len(res) - 1])
          response_data.append(request_results)
          continue

        # 数据库和缓存均没有数据。发起请求,并准备一个空的字典
        request_info = crawler.crawl('https://codeforces.com/api/user.info?handles={}'.format(handle))
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
          request_results['message'] = 'An exception HTTP interface response was encountered: ' + request_info['status']
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
        self.cache_user_info.set(handle, request_results, timeout=30)
        # 存入数据库
        dao.save_user_info(handle, request_results, round(time.time()))
        response_data.append(request_results)
      except Exception as e:
        request_results = {}
        if isinstance(e, requests.exceptions.ConnectionError):
          request_results['success'] = False
          request_results['type'] = 3
          request_results['message'] = 'HTTP interface not responding·'
        else:
          request_results['success'] = False
          request_results['type'] = 4
          request_results['message'] = 'Internal Server Error'
        response_data.append(request_results)
    return response_data
