from flask import Flask, request, jsonify,Response
import urllib.error
import urllib.request
import json
from fake_useragent import UserAgent

app = Flask(__name__)
app.config['DEBUG']=True

def search_handles(handle):
    url = f"https://1codeforces.com/api/user.info?handles={handle}"
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
            return {
                'success':True,
                'handle': handle
            }
        else:
            return {
                'success':True,
                'handle': handle,
                'rating': rating,
                'rank': rank
            }
    except urllib.error.HTTPError as error:
        if error.code == 400:
            return {
                'success': False,
                'type': 1,
                 'message': 'no such handle'
            }
        else:
            return {
                'success': False,
                'type': 2,
                'message': f'HTTP response with code {error.code}',
                'details':{
                        'status':error.code
                }
            }
    except urllib.error.URLError as error:
            return {
                'success': False,
                'type': 3,
                'message': "Nice! Request Failed due to Network issues."
            }
    except Exception as e:
        return {
            'success': False,
            'type': 4,
            'message': str(e)
        }

@app.route('/')
def URL_handles():  # put application's code here
    handles = request.args.get('handles', '').split(',')
    results = []
    for handle in handles:
        result = search_handles(handle)
        results.append(result)
    #会换行但是按照字典序
    # response = jsonify(results)
    # response.headers['Content-Type'] = 'application/json'
    # return response,200
    #不换行但是顺序正确
    return Response(json.dumps(results),mimetype = 'application/json')

if __name__ == '__main__':
    app.run(host = '127.0.0.1',port=2333, debug=True)
