import json

import requests

url = "http://127.0.0.1:2333/clearCache"
headers = {
  'Content-Type': 'application/x-www-form-urlencoded'
}
form_data = 'cacheType=userInfo&handles=a&handles=b'
print(requests.post(url, data=form_data, headers=headers).text)

# headers = {
# 'Content-Type': 'application/json'
# }
# form_data={
# "cacheType": "userRatings",
#   "handles": ['jiangly']
# }
# response = requests.post(url,json=form_data,headers=headers)
# print(response.text)
