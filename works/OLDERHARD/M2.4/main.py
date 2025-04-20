import json
import requests

url = "http://127.0.0.1:2333/clearCache"
headers = {
  'Content-Type': 'application/json'
}
form_data = {
  "cacheType": "userInfo",
  "handles": ['jiangly','zxw'],
  "name":['OLDERHARD']
}

response = requests.post(url, json=form_data, headers=headers)
print(response.text)
