首先进入主目录 /M2.2/xuan81400
***python manage.py runserver 127.0.0.1:2333 这样服务就可以被启动了***
然后就是
在搜索栏中 http://127.0.0.1:2333/?handles=jiangly,zxw,aaabbbccc0,ahz,nnnnnn123 
就能跑了
在 query目录放的是 访问的方法 也是主要的功能实现

query views中放的是实现方法
/xuan81400/xuan81400下面放的是主APP
/xuan81400/xuan81400/urls中放的是对应url的对应解决方法
query目录下的middleware是中间层 在服务器维护期间改变这个可以改变服务器状态
