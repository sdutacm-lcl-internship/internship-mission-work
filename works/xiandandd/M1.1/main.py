import sys
import requests
from lxml import etree
import json


def solve(username):
    url = 'https://codeforces.com/profile/{}/'.format(username)
    response = requests.get(url)
    if response.status_code == 200:
        html = response.content.decode('utf-8')
        root = etree.HTML(html)
        now_rating = root.xpath("//div[@class='info']/ul[1]/li[1]/span[1]/text()")
        max_rating = root.xpath("//div[@class='info']/ul[1]/li[1]//span[@class='smaller']//span[2]/text()")
        contribution = root.xpath("//div[@class='info']//ul/li[2]/span/text()")
        if contribution == []:
            contribution = root.xpath("//div[@class='info']//li[1]/span")
            # contribution也为空说明这个用户不存在
            if contribution == []:
                sys.stderr.write("no such handle\n")
                return 1
        flag = 0
        # 如果为空说明此人没有rank
        if max_rating == []:
            flag = 1
        # 如果有rating，则继续获取这个人的rank
        else:
            rank = root.xpath("//div[@class='user-rank']//span/text()")
        # 如果flag=1，说明这个人没有rating
        if flag == 1:
            data = {
                "name": username
            }
        else:
            data = {
                "name": username,
                "rating": int(now_rating[0]),
                # 去掉最后一个空格
                "rank": rank[0][:-1]
            }
        data_json = json.dumps(data)
        # 输出到标准输出流
        sys.stdout.write(data_json + "\n")
        return 0


def main():
    # 使用sys.argv获取命令行参数
    args = sys.argv[1:]
    for username in args:
        solve(username)


if __name__ == '__main__':
    main()
