from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import json
import requests
import json
import json
import pytz
import re
from .cacheclear import acc
from .models import time_difference
from .models import unix_to_iso

headers = {
    'User-Agent':
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 Edg/113.0.1774.42'
}


def func(handle):
    methodName = "user.rating"
    url = f"https://codeforces.com/api/{methodName}"
    pa = {"handle": handle}
    response = requests.get(url=url, headers=headers, params=pa)
    status = response.status_code
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
        ans.append({"status": status})
    return ans


def func1(handle):
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


list_new = {}
list_old = {}


def ask_mul(request):
    r = request.GET.get("handles", "")
    string = ""
    from datetime import datetime
    current_time = datetime.now()
    ans = []
    r = r + ','
    for i in r:
        if i == ',':
            if string in list_old:
                tmp = list_old[string]
                time = tmp[1]
                if time_difference(time, current_time) == 0:
                    ans.append(tmp[0])
                else:

                    del list_old[string]
                    ans.append(solve1(string, current_time))
            else:
                ans.append(solve1(string, current_time))
            string = ""

        else:
            string = string + i
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
    list_old[string] = lis
    return ans


def ask(request):
    from datetime import datetime
    current_time = datetime.now()
    handle = request.GET.get('handle')
    if handle in list_new:
        ans = list_new[handle]
        code = ans[2]
        time = ans[1]
        if time_difference(time, current_time) == 0:
            t_list = ans[0]
            code = ans[2]
            return JsonResponse(t_list, safe=False, status=code)
        else:

            del list_new[handle]
            return JsonResponse(solve(request, current_time))

    else:
        return solve(request, current_time)


def add_base(tmp_list, status, current_time, dir):
    tmp_list.append(dir)
    tmp_list.append(current_time)
    tmp_list.append(status)
    return tmp_list


def solve(request, current_time):
    handle = request.GET.get('handle')
    tmp_list = []
    try:
        dir = func(handle)
        if len(dir) == 1:
            tmp_list = add_base(tmp_list, 404, current_time, dir)
            list_new[handle] = tmp_list
            return JsonResponse(dir, safe=False, status=404)
        elif len(dir) == 2:
            a = dir[1]["status"]
            tmp_list = add_base(tmp_list, a, current_time, dir)
            list_new[handle] = tmp_list
            return JsonResponse(dir, safe=False, status=a)
        else:
            del dir[-1]
            tmp_list = add_base(tmp_list, 200, current_time, dir)
            list_new[handle] = tmp_list
            return JsonResponse(dir, safe=False, status=200)
    except BaseException as e:
        ans = {'message': "异常"}
        tmp_list = add_base(tmp_list, 500, current_time, ans)
        list_new[handle] = tmp_list
        return JsonResponse(ans, safe=False, status=500)


ans_error = {"message": "invalid request"}
ans = {"message": "ok"}


def clear_all(cache_type):
    if cache_type == "userInfo":
        list_old.clear()
        return JsonResponse(ans, safe=False, status=200)

    elif cache_type == "userRatings":
        list_new.clear()
        return JsonResponse(ans, safe=False, status=200)
    else:

        return JsonResponse(ans_error, safe=False, status=400)


def solve_json(request):
    try:
        data = json.loads(request.body)
        cache_type = data.get('cacheType')
        handles = data.get('handles', None)
    except:
        return JsonResponse(ans_error, safe=False, status=400)
    if len(data) == 1:
        return clear_all(cache_type)
    elif handles == None:
        return JsonResponse(ans_error, safe=False, status=400)
    if isinstance(handles, list):

        return clear_cache(handles, cache_type)
    else:
        return JsonResponse(ans_error, safe=False, status=400)


def solve_x(request):
    try:
        data = request.POST
        cache_type = data.get('cacheType')
        handles = data.get('handles')
    except:
        return JsonResponse(ans_error, safe=False, status=400)

    if len(data) == 1:
        return clear_all(cache_type)
    handles = data.getlist('handles')
    handles_all = []
    handles_all.extend(handles)
    handles_0 = data.getlist('handles[]')
    handles_all.extend(handles_0)
    tmp = []
    pattern = r"handles\[\d+\]"
    for key, value in data.items():
        matches = re.findall(pattern, key)
        if len(matches) != 0:
            tmp.append(value)
    handles_all.extend(tmp)
    if len(data) != 1 and len(handles_all) == 0:
        return JsonResponse(ans_error, safe=False, status=400)

    return clear_cache(handles_all, cache_type)


def solve_ask(request):
    if request.method != 'POST':
        ans = {"message": "invalid request"}
        return JsonResponse(ans, safe=False, status=400)
    if request.content_type == 'application/json':

        return solve_json(request)
    elif request.content_type == 'application/x-www-form-urlencoded':
        return solve_x(request)
    else:
        return JsonResponse({'message': 'invalid request'}, status=400)


def clear_cache(handles, cache_type):
    if cache_type == "userInfo":
        for i in handles:
            if i in list_old:
                del list_old[i]

        return JsonResponse(ans, safe=False, status=200)

    elif cache_type == "userRatings":
        for i in handles:
            if i in list_new:
                del list_new[i]

        return JsonResponse(ans, safe=False, status=200)
    else:

        return JsonResponse(ans_error, safe=False, status=400)


def tet(request):  #这是测试后面4.1的不用的
    return acc()


def user_query(request):
    return render(request, "test.html")
