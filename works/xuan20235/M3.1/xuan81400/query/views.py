from asyncio import Handle
from cmath import exp
from operator import truediv
from pickle import TRUE
from wsgiref import handlers
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import json
import requests
import json
import json
from .cacheclear import acc
from .models import time_difference
from .models import unix_to_iso
import os

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
                "type": '2',
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
                    "success": "True",
                    "result": {
                        "handle": handle,
                        "rating": rate,
                        "rank": rank.strip(),
                    }
                }
                return ans
            else:
                ans = {
                    "success": "True",
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



def solve1(handle):
    from datetime import datetime
    current_time = datetime.now()
    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        ans = func1(handle)
        res = {"handle": handle, "now": current_time, "res": ans}
    except:
        ans = {"success": 'false', "type": 3, "message": "Request timeout"}
        res = {"handle": handle, "now": current_time, "res": ans}
    return res, 200


def ask_file(request):
    handle = request.GET.get('handle')
    return get_rating_from_file(handle)


def ask_mul_file(request):

    r = request.GET.get("handles", "")
    string = ""
    r = r + ','
    handles = []
    for i in r:
        if i == ',':
            handles.append(string)
            string = ""
            continue
        string = string + i
    return get_info_from_file(handles)


cnt = 0  #防卡死
cnt1 = 0
cnt2 = 0
cnt3=0

def get_info_from_file(handles):
   # return HttpResponse(handles)
    file_path = 'data-user-info.txt'
    ans = []
    if os.path.exists(file_path) == 0:
       # return HttpResponse(handles)
        try :
              lis=["yuanshen"]
              res = solve1(lis)
              fp = open(file_path, 'w', encoding='utf-8')
              #a='}'
              fp.write(str(res[0]))
              fp.close()
              cnt = cnt + 1
        except: get_info_from_file(handles)
  
        #return JsonResponse({"message": "文件无法创建"}, safe=False, status=403)
    try:
       # return HttpResponse(handles)
        cnt=0
        for handle in handles:
            fp = open(file_path, 'r', encoding='utf-8')
            page_text = fp.read()
            fp.close()
            page_text = page_text.split(';')
            list = page_text
            flag = 0
            for index, i in enumerate(list):
               # return HttpResponse(i)
                i = i.replace("'", "\"")
                dirc = json.loads(i)
                time = dirc['now']
               # return HttpResponse(i)
                from datetime import datetime
                time_date = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
                current_time = datetime.now()
                #return HttpResponse(handles)
                #return HttpResponse(i)
                if dirc['handle'] == handle:

                    if time_difference(time_date, current_time):
                        res = solve1(handle)
                        if res[1] != 200 and res[1] != 400:
                            ans.append(res['res'])
                            flag = 1
                            break
                        current_time = datetime.now()
                        current_time = current_time.strftime(
                            "%Y-%m-%d %H:%M:%S")
                        res[0]["now"] = current_time
 
                        page_text[index] = str(res[0])
                        fp = open(file_path, 'w', encoding='utf-8')
                        fp.write(str(';'.join(map(str, page_text))))
                        fp.close()
                        #return HttpResponse(res)
                        if res[0]['res']['success']=='True':
                          res[0]['res']['success']=True
                        else :
                          res[0]['res']['success']=False
                        ans.append(res[0]['res'])
                        flag = 1
                        break
                    else:

                        if dirc['res']['success']=='True':
                          dirc['res']['success']=True
                        else :
                          dirc['res']['success']=False
                        ans.append(dirc['res'])
                        flag = 1
           # return HttpResponse(222222)
            if flag == 0:
                res = solve1(handle)
                fp = open(file_path, 'a', encoding='utf-8')
                fp.write(";" + str(res[0]))
                fp.close()
                if res[0]['success']=='True':
                        res[0]['success']=True
                else :
                      res[0]['success']=False
                ans.append(res[0]['res'])
                ans.append(res[0]['res'])

    except Exception as e:
       # return HttpResponse(e)
        cnt=cnt+1
        if cnt<1000:
            return get_info_from_file(handles)  #这里经常报错 我就多试几次来解决了
        return JsonResponse({"message": "程序怎么又异常了"}, safe=False, status=403)
    #ans[]
    return JsonResponse(ans, safe=False, status=200)


def solve(handle):

    from datetime import datetime
    current_time = datetime.now()
    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    try:
        dir = func(handle)
        if len(dir) == 1:
            ans = {"handle": handle, "now": current_time, "res": dir}
            return ans, 400
        elif len(dir) == 2:
            a = dir[1]["status"]
            ans = {"handle": handle, "now": current_time, "res": dir}
            return ans, a
        else:
            del dir[-1]
            ans = {"handle": handle, "now": current_time, "res": dir}
            return ans, 200
    except BaseException as e:
        dir = {"message": "异常"}
        ans = {"handle": handle, "now": current_time, "res": dir}
        return ans, 403


def get_rating_from_file(handle):
    file_path = 'data-user-ratings.txt'
    if os.path.exists(file_path) == 0:
        #return HttpResponse(2222)
        res = solve("yaunshen")
        fp = open(file_path, 'w', encoding='utf-8')
        fp.write(str(res[0]))
        fp.close()
        cnt2 = cnt2 + 1
        if cnt2 < 1000:
            return get_rating_from_file(handle)
        else:
            return JsonResponse({"message": "无法创建文件"}, safe=False, status=500)
    try:
        cnt2=0
        fp = open(file_path, 'r', encoding='utf-8')
        page_text = fp.readline()
        fp.close()
        page_text = page_text.split(";")
        list = page_text
        for index, i in enumerate(list):
            i = i.replace("'", "\"")
            dirc = json.loads(i)
            time = dirc['now']
            from datetime import datetime
            time_date = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.now()
            if dirc['handle'] == handle:
                if time_difference(time_date, current_time):
                    res = solve(handle)
                    if res[1] != 200 and res[1] != 400:
                        return JsonResponse(res[0]['res'],
                                            safe=False,
                                            status=res[1])
                    current_time = datetime.now()
                    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    res[0]["now"] = current_time
                    page_text[index] = str(res[0])
                    fp = open(file_path, 'w', encoding='utf-8')
                    fp.write(str(';'.join(map(str, page_text))))
                    fp.close()
                    return JsonResponse(dirc['res'], safe=False, status=200)
                else:

                    return JsonResponse(dirc['res'], safe=False, status=200)

        res = solve(handle)
        if res[1] != 200:
            JsonResponse(res[0]['res'], safe=False, status=res[1])
        fp = open(file_path, 'a', encoding='utf-8')
        fp.write(";" + str(res[0]))
        fp.close()
        JsonResponse(res[0]['res'], safe=False, status=res[1])

    except Exception as e:
        cnt2=cnt2+1
        if cnt2<1000:
            return  get_rating_from_file(handle)

        else :
            return JsonResponse({"message": "Internal Server Error"},
                            safe=False,
                            status=403)


def tet(request):  #这是测试后面4.1的不用的
    return acc()


def user_query(request):
    return render(request, "test.html")
