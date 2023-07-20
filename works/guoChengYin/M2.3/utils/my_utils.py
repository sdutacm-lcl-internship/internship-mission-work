import json

import requests





class Crawler:
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/57.36'
  }

  def __init__(self):
    pass

  def crawl(self, url):
    try:
      response = requests.get(url=url, headers=self.headers)
      result_json = dict()
      # 若成功爬取
      if response.status_code == 200:
        result_json = json.loads(response.text)
        print(result_json)
        result_json["status"] = 200
      else:
        result_json["status"] = response.status_code
      return result_json
    except Exception as e:
      raise
class MyCache:
  def __init__(self, key, values, timeout):
    buffer = {}


