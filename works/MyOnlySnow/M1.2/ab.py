import urllib.request
import json
import sys
import urllib.parse
from fake_useragent import UserAgent


def resolve(handle):
    real_handle = urllib.parse.quote(handle)
    url = "https://codeforces.com/api/user.info?handles={}".format(real_handle)
    ua = UserAgent().random
    headers = {'User-Agent': ua}
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(request)
    if response.code == 200:
        content = response.read().decode("utf-8")
        Json = json.loads(content)
        info_list = Json.get('result', [])
        if not info_list:
            print("No Such Handle\n")
            exit(1)
        info = info_list[0]
        handle = info.get('handle', '')
        rating = info.get('rating', 0)
        rank = info.get('rank', '')
        max = info.get('maxRating', '')
        if not rank:
            data = {
                'name': handle,
                'rating': rating,
                'rank': 'None'
            }
        if not rating or max == []:
            data = {
                'name': handle,
                'rating': 'None',
                'rank': 'None'
            }
        else:
            data = {
                'name': handle,
                'rating': rating,
                'rank': rank
            }
        print(json.dumps(data) + '\n')
    else:
        print('NetWork error' + response.code + '\n')


def main():
    elements = sys.argv[1:]
    for handle in elements:
        resolve(handle.strip())


if __name__ == '__main__':
    main()
