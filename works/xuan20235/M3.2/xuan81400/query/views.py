from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import json
import requests
import json
import json
from .cacheclear import acc
from .cacheclear import time_difference
from .cacheclear import unix_to_iso
from .cacheclear import shift_time
import os
import pytz
from .models import user_info
from .models import user_rating

from django.db.models.functions import Trunc

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
                "success": False,
                "type": 2,
                "message": f"HTTP response with code {status_code_value}",
                "details": {
                    "status": status_code_value
                }
            }
            return ans
        load_json = json.loads(response.text)
        if load_json["status"] == 'FAILED':
            ans = {"success": False, "type": "1", "message": "no such handle"}
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
            "success": False,
            "type": '3',
            "message": "Internal Server Error"
        }
        return ans
    except BaseException as e:
        ans = {
            "success": False,
            "type": "4",
            "message": 'Internal Server Error'
        }
        return ans


def solve1(handle):

    try:
        ans = func1(handle)
        return ans, 200
    except:
        ans = {"success": False, "type": 3, "message": "Request timeout"}
        return ans, 400


def solve(handle):

    from datetime import datetime
    current_time = datetime.now()
    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        dir = func(handle)
        if len(dir) == 1:
            return dir, 400
        elif len(dir) == 2:
            a = dir[1]["status"]
            return dir, a
        else:
            del dir[-1]
            return dir, 200
    except BaseException as e:
        dir = {"message": "异常"}
        return dir, 500


def ask_sql(request):
    handle = request.GET.get('handle')
    return get_user_rating(handle)


def add_sql(ans, handle, rat):
    date = {
        "handle": handle,
        "contestId": rat.contest_id,
        "contestName": rat.contest_name,
        "rank": rat.rank,
        "ratingUpdatedAt": rat.rating_updated_at,
        "oldRating": rat.old_rating,
        'newRating': rat.new_rating
    }
    ans.append(date)


def get_user_rating(handle):
    ans = []
    handles = []
    handles.append(handle)
    info = get_user_info(handles, 2)
    if info.rating == -1:  #这里并不是武断的直接返回而且已经更新了info发现他还是没有rating或者还是没有这个人
        answer = {"message": "no such handle"}
        return JsonResponse(answer, safe=False, status=404)
    if info.rating == -2:
        answer = {
            "success": True,
            "result": {
                "handle": handle,
            }
        }
        return JsonResponse(answer, safe=False, status=404)
    from datetime import datetime
    user_ratings = user_rating.objects.filter(handle_id=handle)
    current_time = shift_time(datetime.now())

    try:
        #return HttpResponse(20000)
        time1 = shift_time(user_ratings[len(user_ratings) - 1].updated_at)
        if time_difference(time1, current_time):
            #return HttpResponse(current_time)
            res = solve(handle)
            res = res[0]
            cnt = 0
            for rat in user_ratings:
                rat.rank = res[cnt]['rank']
                rat.updated_at = current_time
                rat.old_rating = res[cnt]['oldRating']
                rat.new_rating = res[cnt]['newRating']  #我记得其他的应该都不会变
                cnt = cnt + 1
                rat.save()
                add_sql(ans, handle, rat)
            if len(res) > len(user_ratings):
                for ans in res[len(user_ratings)]:
                    rat = user_rating(handle=handle,
                                      contest_id=ans['contestId'],
                                      contest_name=ans['contestName'],
                                      rank=ans['rank'],
                                      old_rating=ans['oldRating'],
                                      new_rating=ans['newRating'],
                                      rating_updated_at=ans['ratingUpdatedAt'],
                                      updated_at=datetime.now())
                    rat.save()
                    add_sql(ans, handle, rat)
        else:
            for rat in user_ratings:
                add_sql(ans, handle, rat)

    except Exception as e:
        res = solve(handle)
        res = res[0]
        try:
            for an in res:
                rat = user_rating(handle=info,
                                  contest_id=an['contestId'],
                                  contest_name=an['contestName'],
                                  rank=an['rank'],
                                  old_rating=an['oldRating'],
                                  new_rating=an['newRating'],
                                  rating_updated_at=an['ratingUpdatedAt'],
                                  updated_at=datetime.now())
                rat.save()
                add_sql(ans, handle, rat)
        except Exception as e:
            ans = {"message": '又错了已黑化'}
            return JsonResponse(ans, safe=False, status=403)
    return JsonResponse(ans, safe=False, status=200)


def ask_mul_sql(request):
    ans = []
    handles = []
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
    try:
        ans = get_user_info(handles, 1)
    except Exception as e:
        return HttpResponse(e)
    return JsonResponse(ans, safe=False, status=200)


def get_user_info(handles, jd):
    ans = []
    from datetime import datetime
    current_time = datetime.now()
    for handle in handles:
        try:
            info = user_info.objects.get(handle=handle)
            data = {
                'handle': info.handle,
                'rating': info.rating,
                'rank': info.rank,
            }
            time1 = shift_time(info.updated_at)
            current_time = shift_time(datetime.now())
            try:
                if time_difference(time1, current_time):
                    res = solve1(handle)
                    current_time = datetime.now()
                    if "result" in res[0]:
                        answer = res[0]['result']
                        if 'rating' in answer:
                            info.rating = answer['rating']
                            info.rank = answer['rank']
                            info.updated_at = current_time
                        else:
                            info.updated_at = current_time
                        info.save()
                        ans.append(res[0])
                    else:
                        info.updated_at = current_time
                        ans.append(res[0])

                else:
                    if info.rating == -2:
                        answer = {
                            "success": True,
                            "result": {
                                "handle": handle
                            },
                        }
                        ans.append(answer)
                    elif info.rating == -1:
                        answer = {
                            "success": False,
                            "type": "1",
                            "message": "no such handle"
                        }
                        ans.append(answer)
                    else:
                        answer = {"success": True, "result": data}
                        ans.append(answer)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return HttpResponse(e)

        except Exception as e:
            current_time = datetime.now()
            res = solve1(handle)
            answer = {}
            if "result" in res[0]:
                answer = res[0]['result']

                if 'rating' in answer:
                    new = user_info.objects.create(handle=answer['handle'],
                                                   rating=answer['rating'],
                                                   rank=answer['rank'],
                                                   updated_at=current_time)
                else:
                    new = user_info.objects.create(handle=answer['handle'],
                                                   rating=-2,
                                                   updated_at=current_time)
                ans.append(res[0])
            else:
                new = user_info.objects.create(handle=handle,
                                               rating=-1,
                                               updated_at=current_time)
                ans.append(res[0])
    if jd == 1:
        return ans
    else:
        info = user_info.objects.get(handle=handles[0])
        return info


def tet(request):  #这是测试后面4.1的不用的
    return acc()


def user_query(request):
    return render(request, "test.html")
