from multiprocessing.connection import answer_challenge
import flask
import sqlite3
from flask import Flask, request, Response, make_response
import requests
import json
from datetime import timedelta, datetime
import pytz
import py

headers = {
    'User-Agent':
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36 Edg/113.0.1774.42'
}


def get_user_info(handle):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
        SELECT rating,rank FROM user_info
        WHERE handle = ? AND updated_at > ?
        ''', (handle, (datetime.now(pytz.timezone('Asia/Shanghai')) -
                       timedelta(seconds=30)).isoformat()))
        row = cursor.fetchone()
        #print(row)
        if row:
            rating, rank = row
            if rating == None:
                ans = {
                    "success": False,
                    "type": "1",
                    "message": "no such handle"
                }
                return ans
            elif rating == 0:
                print("yaunshen")
                data = {
                    "handle": handle,
                }
            else:
                data = {
                    "handle": handle,
                    "rating": rating,
                    "rank": rank,
                }
            ans = {"success": True, "result": data}
            return ans
    ans = func(handle)
    jd_flag = ans[0]
    ans = ans[1]
    #print(jd_flag)
    if jd_flag == 200:
        data = {
            "handle": handle,
            "rating": ans[0],
            "rank": ans[1],
        }
    elif jd_flag == 203:
        data = {
            "handle": handle,
        }
    elif jd_flag == 404:
        ans = {"success": False, "type": "1", "message": "no such handle"}
        return ans
    else:
        ans = {"message": '又错了已黑化'}
        return ans
    ans = {"success": True, "result": data}
    return ans


def func(handle):
    ans = []
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        Json = response.json()
        info_list = Json.get('result', [])
        info = info_list[0]
        handle = info.get('handle', '')
        rating = info.get('rating', '0')
        rank = info.get('rank', '')
        py.update_info(handle, rating, rank)
        ans.append(rating)
        ans.append(rank)
        if rating == '0':
            return 203, ans
        else:
            return 200, ans
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 400:
            py.update_info(handle, None, None)
            return 404, ans
        else:
            return 500, ans
    except Exception:
        return 500, ans


def sovle(handle):
    with sqlite3.connect('cf.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
        SELECT rating,rank FROM user_info
        WHERE handle = ? AND updated_at > ?
        ''', (handle, (datetime.now(pytz.timezone('Asia/Shanghai')) -
                       timedelta(seconds=30)).isoformat()))
        row = cursor.fetchone()
        if row:
            rating, rank = row
            if rating == None:
                return 1
            elif rating == 0:
                return 2
            else:
                return 3
        ans = func(handle)
        jd_flag = ans[0]
        if jd_flag == 200:
            return 3
        elif jd_flag == 203:
            return 2
        elif jd_flag == 404:
            return 1
        else:
            return 0


def get_user_rating(handle):
    jd_flag = sovle(handle)
    ans = {}
    if jd_flag == 1:
        ans = {"message": "no such handle"}
        answer=[]
        answer.append(ans)
        return answer
    elif jd_flag == 0:
        ans = {
            "success": True,
            "result": {
                "handle": handle,
            }
        }
        answer=[]
        answer.append(ans)
        return answer
    else:
        with sqlite3.connect('cf.db') as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
            SELECT contest_id,contest_name,rank,old_rating,new_rating,rating_updated_at FROM user_ratings
            WHERE handle = ? AND updated_at > ?
            ''', (handle, (datetime.now(pytz.timezone('Asia/Shanghai')) -
                           timedelta(seconds=30)).isoformat()))
            rows = cursor.fetchall()
            if rows:
                data = []
                for row in rows:
                    contest_id, contest_name, rank, old_rating, new_rating, rating_updated_at = row
                    data.append({
                        'handle': handle,
                        'contest_id': contest_id,
                        'contest_name': contest_name,
                        'rank': rank,
                        'ratingUpdatedAt': rating_updated_at,
                        'old_rating': old_rating,
                        'new_rating': new_rating
                    })
                return data
            ans = func1(handle)
            data=[]
            data.append(ans)
            return data


def func1(handle):
    ans = {}
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    try:
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        Json = response.json()
        info_list = Json.get('result', [])
        result = []
        for info in info_list:
            contestId = info.get('contestId', 0)
            contestName = info.get('contestName', '')
            rank = info.get('rank', 0)
            ratingUpdateTimeSeconds = info.get('ratingUpdateTimeSeconds', 0)
            oldRating = info.get('oldRating', 0)
            newRating = info.get('newRating', 0)
            time = datetime.fromtimestamp(ratingUpdateTimeSeconds,
                                          pytz.timezone('Asia/Shanghai'))
            ratingUpdatedAt = time.isoformat()
            if contestId:
                py.update_rating(handle, contestId, contestName, rank,
                                 oldRating, newRating, ratingUpdatedAt)
            result.append({
                'handle': handle,
                'contestId': contestId,
                'contestName': contestName,
                'rank': rank,
                'ratingUpdatedAt': ratingUpdatedAt,
                'oldRating': oldRating,
                'newRating': newRating
            })
        if result == []:
            result = {
                "success": True,
                "result": {
                    "handle": handle,
                }
            }
        return result
    except requests.exceptions.HTTPError as error:
        if error.response.status_code == 400:
            ans = {'message': 'no such handle', 'code': 404}
            return ans
        else:
            ans = {
                "success": False,
                "type": 2,
                "message":
                f"HTTP response with code {error.response.status_code}",
                "details": {
                    "status": error.response.status_code
                }
            }
            return ans
    except Exception as error:
        return {'message': "Internal Server Error", 'code': 500}
