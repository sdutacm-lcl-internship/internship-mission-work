from datetime import datetime
from datetime import timedelta


def time_difference(time1, time2):
    # 将字符串时间转换为datetime对象
    datetime1 = datetime.strptime(time1, "%Y-%m-%d %H:%M:%S")
    datetime2 = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")

    # 计算两个时间之间的时间差
    time_difference = time2 - time1
    #if(time_difference.seconds()
    # 定义五分钟的时间间隔
    five_minutes = timedelta(minutes=5)

    # 比较时间差和五分钟的时间间隔
    if time_difference > five_minutes:
        return True
    else:
        return False
