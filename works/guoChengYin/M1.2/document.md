### 1.什么场景适合爬取 HTML？什么场景适合爬取 API？它们分别有什么优劣？

爬取对象为静态网页时爬取HTML即可。

爬取对象为动态网页时，很多数据不存在于网页源代码中而是需要动态地获取，这时需要爬取API。

爬取HTML需要占用更大的内存，同时还需要对整张网页进行定位解析。但是其获取的信息更加全面。可以爬到一些API没有的数据。

爬取API需要占用的内存较少，直接爬取到想要的信息，同时不需要定位解析。但一些数据没有API接口。

###  2.有哪些常见爬虫的异常情况需要考虑？

（1）403 可能是网站意识到爬取行为采取了反爬措施，例如封IP

（2）401 服务端要求用户身份验证

（3）requests.exceptions ConnectTimeout   连接\读取超时

（4）equests.exceptions ConnectionError  未知的服务器

 （5）requests.exceptions ProxyError   s代理连接不上

### 3.常见状态码

200	请求成功

400 	客户端请求报文中有语法错误，服务器无法理解

401	要求用户进行身份验证

403	服务器拒绝执行该请求（通常是察觉到爬虫，网站封禁IP）

404	找不到资源

500	服务器内部错误

### 4.dump,dumps和load,loads

#### 序列化

dump:将dict类型转化为json字符串格式

dumps:将dict类型转化为string

#### 反序列化

load:针对文件句柄，将json格式的字符转换为dict

loads:针对内存对象，将string转换为dict (将string转换为dict)

