from datetime import datetime
from datetime import timedelta
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
#import models
import pytz


def page_not_found(request, exception, template_name='error/404.html'):
    ans = {"message": "域名错误"}
    return JsonResponse(ans, safe=False, status=404)


def page_not_found_500(request, template_name='error/500.html'):
    ans = {"message": "服务器error"}
    return JsonResponse(ans, safe=False, status=500)


def page_not_found_503(request, template_name='error/503.html'):
    ans = {"message": "服务器error"}
    return JsonResponse(ans, safe=False, status=503)


def time_difference(time1, time2):
    from datetime import datetime
    from datetime import timedelta
    time_difference = (time2 - time1)
    time_15_second = timedelta(seconds=15)
    #time_15_second = timedelta(minutes=15) #方便测试
    if time_difference > time_15_second:
        return 1
    else:
        return 0


def shift_time(time1):
    from datetime import datetime
    time1 = time1.strftime('%Y-%m-%d %H:%M:%S')
    time1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
    return time1


#return HttpResponse(info.rating == -1)
def unix_to_iso(unix_time):
    import datetime
    Date_Time = datetime.datetime.fromtimestamp(unix_time,
                                                pytz.timezone('Asia/Shanghai'))
    Iso_Time = Date_Time.isoformat()
    return Iso_Time


def acc():
    return HttpResponse("222")