from django.shortcuts import render

from django.http import JsonResponse
from django.http import HttpResponse
import json
from http.client import responses
from netrc import netrc
import requests
import json
import os
import re
from bs4 import BeautifulSoup
import lxml
import sys
import time
import json


#import chaojiying
def func(handle):
    #exit(1)  测试 情况5
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    methodName = "user.info"
    url_base = f"https://codeforces.com/api/{methodName}"

    pa = {"handles": handle}
    response = requests.get(url=url_base, params=pa, headers=headers)
    #print(response.status_code)
    # if response.status_code != 200 and response.status_code != 400:  #1 解决url 错误 400是没找到通过下面的来处理
    #     #sys.stderr.write(f"status_code ={response.status_code}\n")
    #     return 0
    load_json = json.loads(response.text)
    status_code_value = response.status_code
    if response.status_code != 200 and response.status_code != 400:  #解决
        ans = {
            "success": 'false',
            "type": 2,
            "message": f"HTTP response with code {status_code_value}",
            "details": {
                "status": status_code_value
            }
        }
        return ans

    if load_json["status"] == 'FAILED':
        #sys.stderr.write("no such handle\n")
        #a = "no such handle"
        ans = {"success": "false", "type": "1", "message": "no such handle"}
        return ans
    else:

        load_json = json.loads(response.text)

        result = load_json["result"]

        if 'rating' in result[0]:

            rate = result[0]["rating"]
            rank = result[0]["rank"]
            #for tmp in result[0]["rank"]:
            #    rank = rank + tmp

            ans = {
                "success": True,
                "result": {
                    "handle": handle,
                    "rating": rate,
                    "rank": rank.strip(),
                }
            }
            #res_json = json.dumps(ans)
            #sys.stdout.write(res_json + '\n')
            return ans
        else:
            ans = {
                "success": True,
                "result": {
                    "handle": handle,
                }
            }

            #res_json = json.dumps(ans)
            #sys.stdout.write(res_json + '\n')
            return ans


def server_error(request):  #一开始是想通过函数来实现 但是不知道怎么拿到服务器的状态 就暂时用中间件写了
    ans = {
        'success': 'false',
        'type': 3,
        'message': 'HTTP response with code 503',
        "details": {
            "status": 503
        }
    }
    return HttpResponse(ans)


def listToJson(lst):
    import numpy as np
    keys = [str(x) for x in np.arange(len(lst))]
    list_json = dict(zip(keys, lst))
    str_json = json.dumps(list_json, indent=2,
                          ensure_ascii=False)  # json转为string
    return list_json


def query_handles(request):

    r = request.GET.get("handles", "")
    #status_code = request
    #return HttpResponse(x)
    string = ""

    string = string + ','

    list = []
    r=r+','
    for i in r:
        if i == ',':

            try:
                list.append(func(string))

            except:
                ans = {
                    "success": 'false',
                    "type": 3,
                    "message": "Request timeout"
                }

                list.append(ans)

            string = ""
            continue
        string = string + i

    # data = json.loads(json_str)
    #     merged_data = {**dir, **tmp}
    #merged_json_str = json.dumps(merged_data)
    # json_str = json.dumps(merged_dict)
    return JsonResponse(list, safe=False)
    # return render(request, "test.html", {
    #     "n3": list
    # })  #通过html实现 返回响应码的我list转化成json老是乱码
    #return HttpResponse(list)
    #return JsonResponse(merged_json_str)


def query_handles1(request):

    handles = request.GET.get('handles', '').split(',')
    results = []

    result = {}

    result['success'] = True
    result['result'] = {
        'handle': 'bule',
        'rating': 9999,
        'rank': "bule 天下第一",
    }

    results.append(result)

    return JsonResponse(results, safe=False, status=200)


# if request.method == 'GET':
#     data = json.loads(request.body)
#     handles = data.get("handles", "").split(",")
#     #results = func(handles)
#     #return JsonResponse(results, safe=False)
#     return HttpResponse("。22222")
# else:
#     return JsonResponse({"Only POST requests are supported."})
