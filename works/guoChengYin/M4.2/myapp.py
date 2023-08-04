import json
import pickle

from flask_cors import CORS
from flask_cors import cross_origin
from flask import Flask, request, jsonify, render_template
from flask_caching import Cache
from service.service import Service
from config import Config

app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)
cache_user_info = Cache(app, config={'CACHE_TYPE': 'simple'})
cache_user_ratings = Cache(app, config={'CACHE_TYPE': 'simple'})

service = Service(cache_user_info, cache_user_ratings)


@app.errorhandler(Exception)
def server_error(e):
  error_message = {"message": 'Internal Server Error'}
  return jsonify(error_message), 500


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


@app.route('/requestUserInfo', methods=["GET", "POST"])
@cross_origin(supports_credentials=True)
def request_use_info():
  handle = request.args.get("handle")
  handle = str(handle).strip()
  response_data = {}
  response_data["handle"] = handle
  handles = []
  handles.append(handle)
  info_res = service.batch_get_user_info(handles)[0]
  if info_res.get("success") == False:
    return jsonify(info_res["message"]), 400
  response_data["rating"] = "暂无"
  if "result" in info_res.keys():
    response_data["rating"] = info_res["result"].get("rating", "暂无")
  info_res = service.get_user_ratings(handle)
  if info_res[1] != 200:
    return jsonify(info_res[0]["message"]), info_res[1]

  info_res = info_res[0]
  rating_history = []
  for item in info_res:
    rating = {}
    if not isinstance(item, dict):
      continue
    rating["contestName"] = item["contestName"]
    rating["ratingUpdatedAt"] = item["ratingUpdatedAt"]
    rating["rank"] = item["rank"]
    rating["oldRating"] = item["oldRating"]
    rating["newRating"] = item["newRating"]
    rating_history.append(rating)
  response_data["rating_history"] = rating_history
  response_data["success"] = True
  return jsonify(response_data)


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=2333)
