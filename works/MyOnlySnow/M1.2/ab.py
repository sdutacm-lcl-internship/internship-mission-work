import urllib.request
import json
import sys
import urllib.parse
from fake_useragent import UserAgent
import urllib.error


def resolve(handle):
    real_handle = urllib.parse.quote(handle)
    url = "https://codeforces.com/api/user.info?handles={}".format(real_handle)
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
        if not rank:
            data = {
                'name': handle,
                'rating': rating,
                'rank': 'None'
            }
        if not rating or max == []:
            data = {
                'name': handle
            }
        else:
            data = {
                'name': handle,
                'rating': rating,
                'rank': rank
            }
        print(json.dumps(data) + '\n')
    except urllib.error.HTTPError as error:
        if error.code == 400:
            print("No Such Handle\n")
        elif error.code == 403:
            sys.stderr.write("Access Forbidden: {}".format(error.code) + '\n')
        elif error.code == 503:
            sys.stderr.write("Service Unavailable: {}".format(error.code) + '\n')
        elif error.code == 404:
            sys.stderr.write("Not Found: {}".format(error.code) + '\n')
        else:
            sys.stderr.write("Network Error: {}".format(error.code) + '\n')
        exit(1)
    except urllib.error.URLError as e:
        sys.stderr.write("URL Error: {}\n".format(e.reason))
        exit(1)


def main():
    elements = sys.argv[1:]
    for handle in elements:
        resolve(handle.strip())


if __name__ == '__main__':
    main()
