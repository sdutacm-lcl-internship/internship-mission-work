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

import pytz
import datetime


def unix_to_iso(unix_time):
    Date_Time = datetime.datetime.fromtimestamp(unix_time)
    Iso_Time = Date_Time.isoformat()
    return Iso_Time


#import chaojiying
def func(handle):
    #exit(1)  #测试 情况5

    methodName = "user.rating"
    url = f"https://codeforces.com/api/{methodName}"
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 Edg/113.0.1774.42'
    }

    pa = {"handle": handle}

    response = requests.get(url=url, headers=headers, params=pa)

    status = response.status_code
    #return status
    ans = []
    if status == 200:
        page = response.json()
        for result in page['result']:
            temp = {
                "handle":
                result['handle'],
                "contestId":
                result['contestId'],
                "contestName":
                result['contestName'],
                "rank":
                result['rank'],
                "ratingUpdatedAt":
                unix_to_iso(result['ratingUpdateTimeSeconds']) + "+08:00",
                "oldRating":
                result['oldRating'],
                'newRating':
                result['newRating']
            }
            ans.append(temp)
        ans.append({"status": status})
    elif status == 400:
        ans.append({"message": "no such handle"})
    else:
        ans.append({"message": "HTTP response with code " + str(status)})
        ans.append({{"status": status}})

    return ans


def query_handles(request):

    r = request.GET.get("handles", "")
    #return HttpResponse(r)
    string = ""

    #string = string + ','

    list = []
    r = r + ','
    for i in r:
        if i == ',':

            try:
                dir = func(string)
                #return HttpResponse(string)
                #return HttpResponse(len(dir))
                if len(dir) == 1:

                    list.append(dir)
                elif len(dir) == 2:

                    list.append(dir)
                else:
                    del dir[2]
                    list.append(dir)
                    #return HttpResponse("222")

            except:
                ans = {'message': '程序异常怎么你了'}

                list.append(ans)

            string = ""
            continue
        string = string + i
    #return HttpResponse()
    return JsonResponse(list, safe=False, status=200)


#from django.views.decorators.cache import cache_page


#@cache_page(60 * 5)
def query_getUserRatings(request):
    handle = request.GET.get('handle')
    try:
        dir = func(handle)
        #return HttpResponse(dir)
        #return HttpResponse(len(dir))
        if len(dir) == 1:

            return JsonResponse(dir, safe=False, status=200)
        elif len(dir) == 2:

            a = dir[1]["status"]
            #return HttpResponse(dir[1])
            return JsonResponse(dir, safe=False, status=a)
        else:
            del dir[2]
            return JsonResponse(dir, safe=False, status=200)
            #return HttpResponse("222")
    except:
        ans = {'message': "异常"}
        return JsonResponse(ans, safe=False, status=200)


def query_getUserRatings1(request):
    handle = request.GET.get('handles')
    try:
        dir = func(handle)
        #return HttpResponse(dir)
        #return HttpResponse(len(dir))
        if len(dir) == 1:

            return JsonResponse(dir, safe=False, status=404)
        elif len(dir) == 2:

            a = dir[1]["status"]
            #return HttpResponse(dir[1])
            return JsonResponse(dir, safe=False, status=a)
        else:
            del dir[2]
            return JsonResponse(dir, safe=False, status=200)
            #return HttpResponse("222")
    except:
        ans = {'message': "异常"}
        return JsonResponse(ans, safe=False, status=200)
