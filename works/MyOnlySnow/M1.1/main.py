import sys
import urllib.request
from lxml import etree
import json


def resolve(handle):
    url = "https://codeforces.com/profile/{}/".format(handle)
    headers = {'user-agent': ' Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36'}
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request)
    if response.code == 200:
        content = response.read().decode('utf-8')
        tree = etree.HTML(content)
        now = tree.xpath("//div[@class='info']/ul[1]/li[1]/span[1]/text()")
        max = tree.xpath("//div[@class='info']/ul[1]/li[1]//span[@class='smaller']/span[2]/text()")
        contribution = tree.xpath("//div[@class='info']//ul/li[2]/span/text()")
        rank = tree.xpath( "//div[@id='body']//div[@id='pageContent']//div[@class='userbox']//div[@class='info']//div[@class='user-rank']/span/text()")
        if contribution == []:
            contribution = tree.xpath("//div[@class='info']//li[1]/span/text()")
            if contribution == []:
                sys.stderr.write("No such handle\n")
                sys.exit(1)

        if not now or max == []:
            data = {
                "name": handle
            }
        else:
            if rank:
                data = {
                    "name": handle,
                    "rating": int(now[0]),
                    "rank": rank[0][:-1]
                }
            else:
                data = {
                    "name": handle,
                    "rating": int(now[0]),
                    "rank": "None"
                }
        real_data = json.dumps(data)
        sys.stdout.write(real_data + "\n")
    else:
        sys.stderr.write("Network error" + str(response.code + "\n"))
    return


def main():
    elements = sys.argv[1:]
    for handle in elements:
        resolve(handle.strip())


if __name__ == '__main__':
    main()
