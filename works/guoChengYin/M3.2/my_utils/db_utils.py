import sqlite3
from dbutils.persistent_db import PersistentDB

class DbPools:
  __pool=None
  def __init__(self):
    db_file = 'cf.db'
    init_script_file = 'init_database.sql'
    self.__pool = PersistentDB(sqlite3, database=db_file)
    with open(init_script_file, 'r',encoding='utf-8') as file:
      init_script = file.read()
    with self.__pool.connection() as conn:
      cursor = conn.cursor()
      cursor.executescript(init_script)
      conn.commit()

  def get_connect(self):
    return self.__pool.connection()



