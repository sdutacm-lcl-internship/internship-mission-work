import datetime
import sqlite3
import sys
import time

from bean import UserInfo


class Dao:
  def query_user_info(self, handles):
    conn = sqlite3.connect('cf.db')
    # 获取游标对象
    cursor = conn.cursor()
    sql = "SELECT * FROM user_info WHERE handle IN ({})".format(','.join(['?'] * len(handles)))
    cursor.execute(sql, tuple(handles))

    res = cursor.fetchall()
    res = list(res[0])
    updatated = res[3]
    if self.get_time_diff(updatated) > 30:
      res = []
    conn.close()

    return res

  # def save_user_info(self,):
  #   conn = sqlite3.connect('../cf.db')
  #   # 获取游标对象
  #   cursor = conn.cursor()
  #   for user_info in user_info_list:
  #     user_info.
  #     handle = user_info.get_handle()
  #     rating = user_info.get_rating()
  #     rank = user_info.get_rank()
  #     updated_at = user_info.get_updated_at()
  #     user_info
  #     cursor.execute("insert into user_info (handle, rating,rank,updated_at) VALUES ('{}','{}','{}','{}')".format(handle,rating,rank,updated_at))
  #   conn.commit()
  #   conn.close()

  def save_ratings(self, ratings):
    conn = sqlite3.connect('cf.db')
    cursor = conn.cursor()
    for rating_info in ratings:
      handle = rating_info.get_handle()

      contest_id = rating_info.get_contest_id()
      contest_name = rating_info.get_contest_name()
      rank = rating_info.get_rank()
      old_rating = rating_info.get_old_rating()
      new_rating = rating_info.get_new_rating()
      updated_at = rating_info.get_updated_at()
      cursor.execute(
        "insert into user_rating (handle,contest_id,contest_name,rank,old_rating,new_rating,rating_updated_at,updated_at) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')".
        format(handle, contest_id, contest_name, rank, old_rating, new_rating, updated_at, round(time.time())))
    conn.commit()
    conn.close()

  def query_ratings(self, handle):
    conn = sqlite3.connect('cf.db')
    # 获取游标对象
    cursor = conn.cursor()
    sql = "SELECT * FROM user_rating WHERE handle='{}'".format(handle)
    print(sql)
    cursor.execute(sql)
    res = cursor.fetchall()
    res = [list(item) for item in res]
    result=[]

    if len(res)!=0:
      for item in res:
        if self.get_time_diff(item[8])<30:
          result.append(item)
    conn.close()
    return result

  @classmethod
  def get_time_diff(self, dt):
    print(round(time.time()) - dt)
    return round(time.time()) - dt
