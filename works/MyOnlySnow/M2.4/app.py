from flask import Flask, request, jsonify, Response, make_response
import urllib.error
import urllib.request
import json
from fake_useragent import UserAgent
from datetime import timedelta, datetime
import redis
import time
import pytz

app = Flask(__name__)
app.config['DEBUG'] = True
cache = {}


def search_handles(handle):
  if handle in cache and cache[handle]['out'] > datetime.now():
    return cache[handle]['data']

  url = f"https://codeforces.com/api/user.info?handles={handle}"
  ua = UserAgent().random
  headers = {'User-Agent': ua}
  request = urllib.request.Request(url=url, headers=headers)
  try:
    response = urllib.request.urlopen(request)
    content = response.read().decode("utf-8")
    Json = json.loads(content)
    info_list = Json.get('result', [])
    info = info_list[0]
    handle = info.get('handle', '')
    rating = info.get('rating', 0)
    rank = info.get('rank', '')
    max = info.get('maxRating', '')
    if not rating or max == []:
      data = {
        'success': True,
        'handle': handle
      }
      cache[handle] = {
        'data': data,
        'out': datetime.now() + timedelta(seconds=15)
      }
    else:
      data = {
        'success': True,
        'handle': handle,
        'rating': rating,
        'rank': rank
      }
      cache[handle] = {
        'data': data,
        'out': datetime.now() + timedelta(seconds=15)
      }
    return data

  except urllib.error.HTTPError as error:
    if error.code == 400:
      data = {
        'success': False,
        'type': 1,
        'message': 'no such handle'
      }
      cache[handle] = {
        'data': data,
        'out': datetime.now() + timedelta(seconds=15)
      }
    else:
      data = {
        'success': False,
        'type': 2,
        'message': f'HTTP response with code {error.code}',
        'details': {
          'status': error.code
        }
      }
  except urllib.error.URLError as error:
    data = {
      'success': False,
      'type': 3,
      'message': "Nice! Request Failed due to Network issues."
    }
  except Exception as e:
    data = {
      'success': False,
      'type': 4,
      'message': "Internal Server Error"
    }
  return data


def search_ratings(handle):
  if handle in cache and cache[handle]['out'] > datetime.now():
    return cache[handle]['data']
  url = f"https://codeforces.com/api/user.rating?handle={handle}"
  ua = UserAgent().random
  headers = {'User-Agent': ua}
  request = urllib.request.Request(url=url, headers=headers)
  try:
    response = urllib.request.urlopen(request)
    content = response.read().decode("utf-8")
    Json = json.loads(content)
    info_list = Json.get('result', [])
    result = []
    for info in info_list:
      contestId = info.get('contestId', 0)
      contestName = info.get('contestName', '')
      rank = info.get('rank', 0)
      ratingUpdateTimeSeconds = info.get('ratingUpdateTimeSeconds', 0)
      oldRating = info.get('oldRating', 0)
      newRating = info.get('newRating', 0)
      time = datetime.fromtimestamp(ratingUpdateTimeSeconds, pytz.timezone('Asia/Shanghai'))
      ratingUpdatedAt = time.isoformat()
      result.append(
        {
          'handle': handle,
          'contestId': contestId,
          'contestName': contestName,
          'rank': rank,
          'ratingUpdatedAt': ratingUpdatedAt,
          'oldRating': oldRating,
          'newRating': newRating
        }
      )
      cache[handle] = {
        'data': result,
        'out': datetime.now() + timedelta(seconds=15)
      }
    return result


  except urllib.error.HTTPError as error:
    if error.code == 400:
      data = {
        'message': 'no such handle',
        'code': 404
      }
      cache[handle] = {
        'data': data,
        'out': datetime.now() + timedelta(seconds=15)
      }
      return data
    else:
      return {
        'message': f'HTTP response with code {error.code}',
        'code': error.code
      }
  except urllib.error.URLError as error:
    return {
      'message': "Nice! Request Failed due to Network issues.",
      'code': 503
    }
  except Exception as error:
    return {
      'message': "Internal Server Error",
      'code': error.code
    }


@app.route('/batchGetUserInfo')
def URL_handles():  # put application's code here
  handles = request.args.get('handles', '').split(',')
  results = []
  for handle in handles:
    result = search_handles(handle)
    results.append(result)
  # 会换行但是按照字典序
  # response = jsonify(results)
  # response.headers['Content-Type'] = 'application/json'
  # return response,200
  # 不换行但是顺序正确
  return Response(json.dumps(results), mimetype='application/json')


@app.route('/getUserRatings')
def URL_ratings():
  handle = request.args.get('handle', '')
  results = []
  results = search_ratings(handle)
  if 'message' in results and 'code' in results:
    return json.dumps(results['message']), results['code']
  else:
    return json.dumps(results)


@app.route('/clearCache', methods=['POST'])
def clear_cache():
  try:
    if request.content_type == 'application/json':
      data = request.get_json()
    elif request.content_type == 'application/x-www-form-urlencoded':
      data = request.form.to_dict()
    else:
      return jsonify({'message': 'invalid request'}), 400

    cache_type = data.get('cacheType')
    handles = data.get('handles', [])

    if cache_type not in ('userInfo', 'userRatings'):
      return jsonify({'message': 'invalid request'})

    if not handles:
      cache.pop(cache_type, None)
    else:
      for handle in handles:
        cache_entry = cache.get(cache_type, {}).get(handle)
        if cache_entry:
          del cache[cache_type][handle]

    return jsonify({'message': 'ok'}), 200

  except Exception:
    return jsonify({'message': 'invalid request'}), 400


if __name__ == '__main__':
  app.run(host='127.0.0.1', port=2333, debug=True)
