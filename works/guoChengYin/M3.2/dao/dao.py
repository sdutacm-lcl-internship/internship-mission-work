import sqlite3
import sys
from bean import UserInfo

class Dao:
  def query_user_info(self,handles):
    conn = sqlite3.connect('cf.db')
    # 获取游标对象
    cursor = conn.cursor()
    sql = "SELECT * FROM user_info WHERE handle IN ({})".format(','.join(['?'] * len(handles)))
    cursor.execute(sql,tuple(handles))
    conn.close()
    return list(cursor.fetchall())

  def save_user_info(self,user_info):
    conn = sqlite3.connect('cf.db')
    # 获取游标对象
    cursor = conn.cursor()
    handle = user_info.get_handle()
    rating = user_info.get_rating()
    rank = user_info.get_rank()
    updated_at = user_info.get_updated_at()
    cursor.execute("insert into user_info (handle, rating,rank,updated_at) VALUES ('{}','{}','{}','{}')".
    format(handle,rating,rank,updated_at))
    conn.commit()
    conn.close()


  def save_ratings(self,ratings):
    conn = sqlite3.connect('cf.db')
    cursor = conn.cursor()
    user_rating_id=ratings.get_user_rating_id()
    contest_name=ratings.get_contest_name()
    rank=ratings.get_rank()
    old_rating=ratings.get_old_rating()
    new_rating=ratings.get_new_rating()
    updated_at = ratings.get_updated_at()
    cursor.execute("insert into user_rating (user_rating_id,contest_name,rank,old_rating,new_rating,updated_at) VALUES ('{}','{}','{}','{}','{}','{}')".
                   format(user_rating_id,contest_name,rank,old_rating,new_rating,updated_at))
    conn.commit()
    conn.close()
  def query_ratings(self,handle):
    conn = sqlite3.connect('cf.db')
    # 获取游标对象
    cursor = conn.cursor()
    sql = "SELECT * FROM user_rating WHERE handle={}".format(handle)
    cursor.execute(sql)
    conn.close()
    return list(cursor.fetchall())









