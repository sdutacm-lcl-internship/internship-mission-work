import json

import requests


class Utils:
  def __init__(self):
    pass

  '''
  data_save()文件保存函数
  path:保存路径
  s:保存内容'''

  def data_save(self, path, s):
    with open(path, "r+") as f:
      # 先读取文件数据,并将其转为字典
      file_data = self.read_file(path)

      # 更新选手信息,将数据写入字典
      file_data[s["handle"]] = s["info"]
      # 再将更改的字典，写入文件
      json.dump(file_data, f)

  def read_file(self, path):
    with open(path, "r") as f:
      txt = f.read()
      return json.loads(txt)


'''
爬虫
'''


class Crawler:
  def __init__(self):
    self.headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/57.36'
    }

  def crawl(self, url):
    try:
      response = requests.get(url=url, headers=self.headers)
      result_json = dict()
      # 若成功爬取
      if response.status_code == 200:
        resText = response.text
        if(resText.startswith("<!DOCTYPE html>")):
          result_json["status"] = 502
        else:
          result_json = json.loads(response.text)
          result_json["status"] = 200
      else:
        result_json["status"] = response.status_code
      return result_json
    except Exception as e:
      raise
