import json
import sys

import requests
import parsel
def solve(username):
  url = 'https://codeforces.com/profile/{}'.format(username)
  #伪装成正常访问
  headers = {
    'cookie':'__utmz=71512449.1689222621.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); JSESSIONID=672FB94F0EAC899F8CFC5AA46CA4CFB2-n1; 39ce7=CFvnpm3F; __utma=71512449.943931001.1689222621.1689336095.1689492329.5; __utmc=71512449; __utmt=1; __utmb=71512449.1.10.1689492329; __cf_bm=dzmQglvmP.XChgKtwCF7lXoifRIf6WONlEcxlthpr6s-1689492330-0-AYPajZXVdYcPzBN6bLmx4nDySXz3ZcuYbwOr35kcPQTvzP7cnPgmCMjSgYWPBEHimQ==',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/57.36'
  }

  res = requests.get(url, headers=headers)
  if res.status_code == 200:
    resHtml = res.text
    # 使用parse模块解析html
    selector = parsel.Selector(resHtml)
    # xpath提取网页元素
    rating = selector.xpath('//*[@id="pageContent"]/div[2]/div/div[2]/ul/li[1]/span[1]/text()').get()
    # handleFirst handle首字母
    handleFirst = selector.xpath('//*[@id="pageContent"]/div[2]/div/div[2]/div/h1/a/span/text()').get()
    # handle除首字母外其他部分
    handlePart = selector.xpath('//*[@id="pageContent"]/div[2]/div/div[2]/div/h1/a/text()').get()
    rank = selector.xpath('//*[@id="pageContent"]/div[2]/div/div[2]/div/div[1]/span/text()').get()

    #若handlePart为空则认为不存在该用户
    if handlePart is None:
      sys.stderr.write('no such handle' + "\n")
      return 1

    #如果handle首字母不为空则加入到最终的handle中，否则只取handlePart
    if not handleFirst is None:
      handle = str(handleFirst) + str(handlePart)
    else:
      handle = str(handlePart)

      #rating为空只封装handle
    if rating is None:
      data = {
        "handle":handle
      }
    else:
      data={
        "handle":handle,
        "rating":int(rating),
        "rank":str(rank)
      }

    #封装json数据
    json_data = json.dumps(data)

    #输出
    sys.stdout.write(json_data + "\n")
  else:
    sys.stderr.write("ErrorCode"+str(res.status_code)+'\n')
    return 1

if __name__ == '__main__':
  while True:
    username = input().strip()
    solve(username)
    sys.stdout.write('是否继续程序？【Y/N】'+ "\n")
    decide =  input().strip().upper()
    if  not decide=='Y':
      break



