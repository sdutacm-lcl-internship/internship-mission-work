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
    try:
        response = requests.get(url=url_base, params=pa, headers=headers)
       
        status_code_value = response.status_code

       
        if response.status_code != 200 and response.status_code != 400: 
            ans = {
                "success": 'false',
                "type": 2,
                "message": f"HTTP response with code {status_code_value}",
                "details": {
                    "status": status_code_value
                }
            }
            return ans
        load_json = json.loads(response.text)
        if load_json["status"] == 'FAILED':
     
            ans = {
                "success": "false",
                "type": "1",
                "message": "no such handle"
            }
            return ans
        else:

            load_json = json.loads(response.text)

            result = load_json["result"]

            if 'rating' in result[0]:

                rate = result[0]["rating"]
                rank = result[0]["rank"]
               

                ans = {
                    "success": True,
                    "result": {
                        "handle": handle,
                        "rating": rate,
                        "rank": rank.strip(),
                    }
                }
            
                return ans
            else:
                ans = {
                    "success": True,
                    "result": {
                        "handle": handle,
                    }
                }

             
                return ans

    except requests.exceptions.RequestException as e: 
        ans = {
            "success": 'false',
            "type": '3',
            "message": "Internal Server Error"
        }
        return ans
    except BaseException as e:
        ans = {
            "success": "false",
            "type": "4",
            "message": 'Internal Server Error'
        }
        return ans



def query_handles(request):

    r = request.GET.get("handles", "")
 
    string = ""

    string = string + ','

    list = []
    r = r + ','
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


    return JsonResponse(list, safe=False)
   


