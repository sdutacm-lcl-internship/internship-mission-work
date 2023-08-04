# config.py

import os

# 获取当前文件所在目录的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
  # Flask 应用程序的密钥，用于加密会话等数据
  SECRET_KEY = 'your_secret_key_here'

  # 数据库配置，可以根据实际情况进行修改
  SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  # 将 "dao"、"service"、"my_utils" 目录添加到源代码根目录
  # 这样在应用程序中就可以方便地引用这些目录中的模块
  # 例如: from dao import some_dao_module
  #      from service import some_service_module
  #      from my_utils import some_util_function
  import sys
  sys.path.append(os.path.join(basedir, 'dao'))
  sys.path.append(os.path.join(basedir, 'service'))
  sys.path.append(os.path.join(basedir, 'my_utils'))
