import requests
import json
from urllib.parse import  urlencode
url = "http://127.0.0.1:2333/clearCache"
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
data='cacheType=userInfo&handles%5B0%5D=jiangly&handles%5B1%5D=zxw'
response = requests.post(url, data=data, headers=headers)
print(response.json())
# headers = {'Content-Type': 'application/json'}
# data = {
#   "cacheType": "worldTreeData",
#   "handles": "bLue"
# }
# response = requests.post(url, data=json.dumps(data), headers=headers)
# print(response.json())


