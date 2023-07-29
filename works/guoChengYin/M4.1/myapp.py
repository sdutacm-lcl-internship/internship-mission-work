import json
import pickle

from flask import Flask, request, jsonify, render_template
from flask_caching import Cache
from service.service import Service

app = Flask(__name__, template_folder='templates')

cache_user_info = Cache(app, config={'CACHE_TYPE': 'simple'})
cache_user_ratings = Cache(app, config={'CACHE_TYPE': 'simple'})

service = Service(cache_user_info, cache_user_ratings)


# @app.errorhandler(Exception)
# def server_error(e):
#   error_message = {"message": 'Internal Server Error'}
#   return jsonify(error_message), 500
@app.route('/getUserRatings')
def get_user_ratings():
  handle = request.args.get('handle')
  handle = handle.replace('{', '').replace('}', '')
  res = service.get_user_ratings(handle)
  return jsonify(res[0]), res[1]


@app.route('/batchGetUserInfo')
def get_user_info():
  handles = request.args.get('handles')
  handles = handles.replace('{', '').replace('}', '').split(',')
  user_infos = service.batch_get_user_info(handles)
  return jsonify(user_infos)


@app.route('/')
def show_index():
  return render_template("index.html")


@app.route('/requestUserInfo')
def request_use_info():
  handle = request.args.get("handle")
  response_data = {}
  response_data["handle"] = handle
  info=service.batch_get_user_info(handle)
  print(info)

  return ''


if __name__ == '__main__':
  # 项目启动前先将文件中的数据填充到缓存中

  app.run(host='127.0.0.1', port=2333)
