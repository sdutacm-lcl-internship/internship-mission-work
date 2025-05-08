## Flask + http学习

flask真是便便又利利呢

## 总结

**HTTP 协议的基本组成部分有**：请求行、请求头、请求体和响应行、响应头、响应体。

请求行中包含方法、请求 URI 和 HTTP 版本。例如：GET /users/ahz HTTP/1.1。

请求头中包含请求头名称和请求头参数。例如：Accept-Language: zh-CN,zh;q=0.9。

请求体中包含请求数据。例如：{"username": "ahz", "password": "password"}。

响应行中包含HTTP版本和状态码。例如：HTTP/1.1 200 OK。

响应头中包含响应头名称和响应头参数。例如：Content-Type: application/json。

响应体中包含响应数据。例如：{"success": True, "result": {"handle": "ahz"}}。

**在 HTTP 请求中，常见的传参方式有：**

1. Query Parameters：在 URL 的查询参数部分传递参数。例如：/users?handle=ahz。

2. Body Parameters：将参数放在请求体中。例如：POST /users { "username": "ahz", "password": "password" }。

3. Header Parameters：将参数作为请求头参数传递。例如：GET /users/ahz HTTP/1.1 Host: example.com。

4. Path Parameters：将参数放在请求 URI 的路径部分。例如：GET /users/{handle}。

## 优化方案

1. 多线程
2. 加缓存
3. ~~想不到力~~