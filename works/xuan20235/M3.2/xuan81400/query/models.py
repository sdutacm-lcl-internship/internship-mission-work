from django.db import models

from django.http import JsonResponse
import pytz


class user_info(models.Model):
    handle = models.CharField(primary_key=True, max_length=30)
    rating = models.IntegerField(null=True, blank=True)
    rank = models.CharField(null=True, blank=True, max_length=30)
    updated_at = models.DateTimeField()


class user_rating(models.Model):
    user_rating_id = models.AutoField(primary_key=True)
    handle = models.ForeignKey(user_info, on_delete=models.CASCADE)
    contest_id = models.IntegerField()
    contest_name = models.CharField(max_length=255)
    rank = models.IntegerField()
    old_rating = models.IntegerField()
    new_rating = models.IntegerField()
    rating_updated_at = models.DateTimeField()
    updated_at = models.DateTimeField()


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
