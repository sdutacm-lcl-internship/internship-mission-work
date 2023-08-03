import logging
import sqlite3
import time
from db_utils import DbPools

class Dao:
  def __init__(self):
    self.pool = DbPools()

  def query_user_info(self, handle):
    conn = self.pool.get_connect()
    # 获取游标对象
    cursor = conn.cursor()
    sql = "SELECT * FROM user_info WHERE handle ='{}'".format(handle)
    cursor.execute(sql)
    res = cursor.fetchall()
    if len(res) != 0:
      res = list(res[0])
      updatated = res[3]
      diff = self.get_time_diff(updatated)
      if diff > 30:
        res = []
      else:
        res.append(diff)
    conn.close()
    return res

  def save_user_info(self, handle, user_info, update_at):
    conn = self.pool.get_connect()

    # 获取游标对象
    cursor = conn.cursor()
    rating = user_info["result"].get("rating", 0)
    rank = user_info["result"].get("rank", "")
    cursor.execute("replace into user_info (handle,rating,rank,updated_at) VALUES ('{}','{}','{}','{}')".format(handle, rating, rank,update_at))
    conn.commit()
    conn.close()

  def save_ratings(self, handle, ratings, update_time_at):
    conn = self.pool.get_connect()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    for rating in ratings:
      handle = rating["handle"]
      contest_id = rating["contestId"]
      contest_name = rating["contestName"]
      rank = rating["rank"]
      old_rating = rating["oldRating"]
      new_rating = rating["newRating"]
      updated_at = rating["ratingUpdatedAt"]
      try:
        cursor.execute(
          "insert or replace into user_rating (handle,contest_id,contest_name,rank,old_rating,new_rating,rating_updated_at,updated_at) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')".
          format(handle, contest_id, contest_name, rank, old_rating, new_rating, updated_at, update_time_at))
        conn.commit()
      except Exception as e:
        logging.debug(e)
        conn.rollback()
        conn.close()
        raise


  def query_ratings(self, handle):
    conn = self.pool.get_connect()
    # 获取游标对象
    cursor = conn.cursor()
    sql = "SELECT * FROM user_rating WHERE handle='{}'".format(handle)
    cursor.execute(sql)
    res = cursor.fetchall()
    result = []
    if len(res) != 0:
      diff = self.get_time_diff(res[0][8])
      if diff < 30:
        for item in res:
          result.append({
            "handle": item[1],
            "contestId": item[2],
            "contestName": item[3],
            "rank": item[4],
            "ratingUpdatedAt": item[7],
            "oldRating": item[5],
            "newRating": item[6]
          })
        result.append(diff)
    conn.close()
    return result

  @classmethod
  def get_time_diff(self, dt):
    diff=round(time.time() - dt)
    logging.debug("该数据已经在数据库中存储了:" +str(diff))
    return diff
