import datetime
import sqlite3
import sys
import time


class Dao:
  def query_user_info(self, handle):
    conn = sqlite3.connect('cf.db')
    # 获取游标对象
    cursor = conn.cursor()
    sql = "SELECT * FROM user_info WHERE handle ='{}'".format(handle)
    cursor.execute(sql)
    res = cursor.fetchall()
    print("res")
    print(res)
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
    conn = sqlite3.connect('cf.db')
    # 获取游标对象
    cursor = conn.cursor()
    print(user_info)
    rating = user_info["result"].get("rating", 0)
    rank = user_info["result"].get("rank", "")
    cursor.execute("delete from user_info where handle = '{}'".format(handle))
    cursor.execute(
      "insert into user_info (handle,rating,rank,updated_at) VALUES ('{}','{}','{}','{}')".format(handle, rating, rank,
                                                                                                  update_at))
    conn.commit()
    conn.close()

  def save_ratings(self, handle, ratings, update_time_at):
    conn = sqlite3.connect('cf.db')
    cursor = conn.cursor()
    cursor.execute("delete from user_rating where handle = '{}'".format(handle))
    for rating in ratings:
      handle = rating["handle"]
      contest_id = rating["contestId"]
      contest_name = rating["contestName"]
      rank = rating["rank"]
      old_rating = rating["oldRating"]
      new_rating = rating["newRating"]
      updated_at = rating["ratingUpdatedAt"]
      cursor.execute(
        "insert into user_rating (handle,contest_id,contest_name,rank,old_rating,new_rating,rating_updated_at,updated_at) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')".
        format(handle, contest_id, contest_name, rank, old_rating, new_rating, updated_at, update_time_at))
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

    result = []
    if len(res) != 0:
      diff = self.get_time_diff(res[0][8])
      print(diff)
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
    print("该数据已经在数据库中存储了:", end='')
    diff=round(time.time() - dt)
    return diff
