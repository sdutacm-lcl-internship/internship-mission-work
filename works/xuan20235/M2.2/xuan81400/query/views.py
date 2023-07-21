from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.core.cache import cache
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

#from tests import time_differences
#import tests


def unix_to_iso(unix_time):
    import datetime
    Date_Time = datetime.datetime.fromtimestamp(unix_time,
                                                pytz.timezone('Asia/Shanghai'))
    Iso_Time = Date_Time.isoformat()
    return Iso_Time


#import chaojiying
#@cache_page(60 * 5)
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
                "handle": result['handle'],
                "contestId": result['contestId'],
                "contestName": result['contestName'],
                "rank": result['rank'],
                "ratingUpdatedAt":
                unix_to_iso(result['ratingUpdateTimeSeconds']),
                "oldRating": result['oldRating'],
                'newRating': result['newRating']
            }
            ans.append(temp)
        ans.append({"status": 'OK'})
        if len(ans) == 1:
            ans.append({"result": []})
            ans.append({"message": "no such handle"})  #这是随便加的 为了统一DEL[-1]
    elif status == 400:
        ans.append({"message": "no such handle"})
    else:
        ans.append({"message": "HTTP response with code " + str(status)})
        ans.append({{"status": status}})

    return ans


@cache_page(15)
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


#@cache_page(15)
def query_getUserRatings(request):
    #return HttpResponse(request.path)
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
            #del dir[2]
            del dir[-1]
            return JsonResponse(dir, safe=False, status=200)
            #return HttpResponse("222")
    except BaseException as e:
        #return HttpResponse(e)

        ans = {'message': "异常"}
        return JsonResponse(ans, safe=False, status=500)


def func1(handle):
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


def query_handles1(request):

    r = request.GET.get("handles", "")

    string = ""

    string = string + ','

    list = []
    r = r + ','
    for i in r:
        if i == ',':

            try:
                list.append(func1(string))

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


#from datetime import timedelta
#from datetime import datetime
#from datetime import datetime
#from datetime import datetime


def time_difference(time1, time2):
    # 将字符串时间转换为datetime对象
    from datetime import datetime
    from datetime import timedelta
    # datetime1 = datetime(time1, "%Y-%m-%d %H:%M:%S")
    # datetime2 = datetime(time2, "%Y-%m-%d %H:%M:%S")

    # 计算两个时间之间的时间差
    time_difference = (time2 - time1)
    # 定义五分钟的时间间隔
    five_minutes = timedelta(minutes=5)

    # 比较时间差和五分钟的时间间隔
    if time_difference > five_minutes:
        return 1
    else:
        return 0


#from datetime import datetime

list = {}
list_old = {}


def ask_mul(request):

    r = request.GET.get("handles", "")
    string = ""
    #return HttpResponse(r)
    from datetime import datetime
    current_time = datetime.now()
    tmp_list = []
    #list = []
    ans = []
    r = r + ','
    #return HttpResponse(r)

    for i in r:
        if i == ',':
            if string in list_old:
                #ans = list[string]
                tmp = list_old[string]
                #code = ans[2]
                #nam_list.append(string)
                time = tmp[1]
                if time_difference(time, current_time) == 0:
                    #t_list = ans[0]
                    ans.append(tmp[0])
                    #return JsonResponse(ans[0])
                    #return HttpResponse(string)
                else:

                    del list_old[string]
                    ans.append(solve1(string, current_time))
            else:
                ans.append(solve1(string, current_time))
            string = ""

        else:
            string = string + i
            #return HttpResponse(string)
    #return HttpResponse(list)
    return JsonResponse(ans, safe=False, status=200)


def solve1(string, current_time):
    lis = []
    try:
        ans = func1(string)
        lis.append(ans)
        lis.append(current_time)

    except:
        ans = {"success": 'false', "type": 3, "message": "Request timeout"}
        lis.append(ans)
        lis.append(current_time)
    #del list[string]
    list_old[string] = lis
    return ans


def ask(request):
    from datetime import datetime
    current_time = datetime.now()
    handle = request.GET.get('handle')

    tmp_list = []

    if handle in list:
        ans = list[handle]
        code = ans[2]
        time = ans[1]

        if time_difference(time, current_time) == 0:
            #return HttpResponse(2000)

            # del ans[1]  # 1放时间 2是状态码’
            # del ans[1]
            t_list = ans[0]
            code = ans[2]
            return JsonResponse(t_list, safe=False, status=code)
        else:

            del list[handle]
            return solve(request, tmp_list, current_time)

    else:
        return solve(request, tmp_list, current_time)


def solve(request, tmp_list, current_time):
    handle = request.GET.get('handle')
    try:
        dir = func(handle)
        #return HttpResponse(dir)
        #return HttpResponse(len(dir))
        if len(dir) == 1:

            tmp_list.append(dir)
            tmp_list.append(current_time)
            tmp_list.append(200)
            list[handle] = tmp_list
            return JsonResponse(dir, safe=False, status=200)
        elif len(dir) == 2:

            a = dir[1]["status"]
            tmp_list.append(dir)
            tmp_list.append(current_time)
            tmp_list.append(a)
            list[handle] = tmp_list
            return JsonResponse(dir, safe=False, status=a)
        else:
            #del dir[2]

            del dir[-1]
            tmp_list.append(dir)
            tmp_list.append(current_time)
            tmp_list.append(200)
            list[handle] = tmp_list
            return JsonResponse(dir, safe=False, status=200)
            #return HttpResponse("222")
    except BaseException as e:
        #return HttpResponse(e)

        ans = {'message': "异常"}
        tmp_list.append(ans)
        tmp_list.append(current_time)
        tmp_list.append(500)
        list[handle] = tmp_list
        return JsonResponse(ans, safe=False, status=500)


def clearCache(request, handles=None):
    cache_type = request.POST.get("cacheType")
    if cache_type == 'userInfo':
        #return HttpResponse("222")
        r = request.POST.getlist('handles')
        ans = {"message": "ok"}

        if len(r) == 0:
            list_old.clear()
            return JsonResponse(ans, safe=False, status=200)
        for i in r:

            if i in list_old:
                del list_old[i]

        return JsonResponse(ans, safe=False, status=200)
    elif cache_type == 'userRatings':
        ans = {"message": "ok"}
        r = request.POST.getlist('handles')

        if len(r) == 0:
            list.clear()
            return JsonResponse(ans, safe=False, status=200)
        for i in r:

            if i in list:
                del list[i]

        return JsonResponse(ans, safe=False, status=200)

    else:
        # 不支持的缓存类型

        ans = {"message": "invalid request"}
        return JsonResponse(ans, safe=False, status=404)
