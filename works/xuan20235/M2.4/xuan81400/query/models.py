from django.db import models

from django.http import JsonResponse
import pytz


class user_info(models.Model):
    handle = models.CharField(primary_key=True, max_length=30)
    rating = models.IntegerField(null=True, blank=True)
    rank = models.CharField(null=True, blank=True, max_length=30)
    updated_at = models.DateTimeField()


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


def unix_to_iso(unix_time):
    import datetime
    Date_Time = datetime.datetime.fromtimestamp(unix_time,
                                                pytz.timezone('Asia/Shanghai'))
    Iso_Time = Date_Time.isoformat()
    return Iso_Time


# class UserRating(models.Model):
#     user_rating_id = models.AutoField(primary_key=True)
#     handle = models.ForeignKey(user_info.handle, on_delete=models.CASCADE)
#     contest_id = models.IntegerField()
#     contest_name = models.CharField(max_length=255)
#     rank = models.IntegerField()
#     old_rating = models.IntegerField()
#     new_rating = models.IntegerField()
#     rating_updated_at = models.DateTimeField()
#     updated_at = models.DateTimeField()

# Create your models here.
# * ......................我佛慈悲......................
#  *                      _oo0oo_
#  *                     o8888888o
#  *                     88" . "88
#  *                     (| -_- |)
#  *                     0\  =  /0
#  *                    ___/`---'\___
#  *                  .' \\|     |// '.
#  *                 /  \\|||  :  |||// \
#  *                / _  ||||| -卍-|||||- \
#  *               |   | \\\  -  /// |   |
#  *               | \_|    ''\---/''  |_/ |
#  *               \  .- \__  '-'  ___/-. /
#  *             ___'. .'     /--.--\   `. .'___
#  *          ."" '<  `.    ___\_<|>_/___.' >' "".
#  *         | | :  `  - \`.;`\ _ /`;.`/ - ` : | |
#  *         \  \ `_      \_ __\ /__ _/   .-` /  /
#  *     =====`-.____`.___ \_____/___.-`___.-'===== `=---=' `=---=' `=---='
#  *                       `=---='
#  *
#  *..................佛祖开光 ,永无BUG...................
#  *
# ————————————————
