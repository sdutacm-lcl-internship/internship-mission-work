import sys
import json
import requests
import re


def grep_rank(handle):
    url = 'https://codeforces.com/profile/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 Edg/113.0.1774.42'
    }
    # handle = input()
    url = url + handle
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        page_text = response.text
        find_rank = re.compile(r'div class="user-rank">(.*?)</div>', re.S)
        find_rankname = re.compile(r'<span .*?>(.*?) </span>')
        rank_list = re.findall(find_rank, page_text)
        if len(rank_list) == 0:
            sys.stderr.write("no such handle\n")
            exit(1)
        else:
            rank = re.findall(find_rankname, rank_list[0])[0]
            find_rating = re.compile(r'<span style="font-weight:bold;" class="user-.*?>(.*?)</span>', re.S)
            rating_list = re.findall(find_rating, page_text)
            if len(rating_list) == 0:
                ans = {
                    'handle': handle,
                }
            else:
                ans = {
                    'handle': handle,
                    'rating': int(rating_list[0]),
                    'rank': rank,
                }
            ans_json = json.dumps(ans)
            sys.stdout.write(ans_json + '\n')
            return 0


def main():
    handles = sys.argv[1:]
    for handle in handles:
        grep_rank(handle)
    # solve()


if __name__ == "__main__":
    main()
