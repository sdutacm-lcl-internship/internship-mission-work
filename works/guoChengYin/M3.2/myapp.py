import json

import myapp as myapp
from flask import Flask, request, jsonify
from flask_caching import Cache
from service.service import Service
app = Flask(__name__)


cache_user_info = Cache(app, config={'CACHE_TYPE': 'simple'})
cache_user_ratings = Cache(app, config={'CACHE_TYPE': 'simple'})

service=Service(cache_user_info,cache_user_ratings)
@app.route('/getUserRatings')
def get_user_ratings():
  handle = request.args.get('handle')
  handle = handle.replace('{', '').replace('}', '')
  ratings=service.get_user_ratings(handle)
  for item in ratings:
    item=item.__str__()
  print(ratings)


  return json.dumps(ratings)




def load_cache():
  pass


if __name__ == '__main__':
  # 项目启动前先将文件中的数据填充到缓存中
  load_cache()
  app.run(host='127.0.0.1', port=2333)
