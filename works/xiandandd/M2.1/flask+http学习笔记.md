# python后端轻量级框架--flask

## 下载：

pip install flask

## 一段简单的代码-在网页输出hello world！

```python
from flask import Flask
app = Flask(__name__)#创建一个Flask应用程序实例

@app.route('/')#当访问这个路径的时候，执行以下函数体
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run('0.0.0.0')#调用app的run方法即可启动服务，指定’0.0.0.0’,这会让操作系统监听所有公网 IP，不要忘了引号
#若想要指定端口号的话，应该这么写：app.run('127.0.0.1',port=2333)

```

## 为朴素的页面添加样式

### 方法一：直接返回html代码，简单粗暴，但是麻烦

注意缩进

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def hello_world():
    def index():
        user = {'username': '咸蛋dd'}
        return '''
            <html>
                <head>
                    <title>Home Page - CSDN</title>
                </head>
                <body>
                    <h1 style="color:red">Hello, ''' + user['username'] + '''!</h1>
                </body>
            </html>'''
    return index()

if __name__ == '__main__':
    app.run('0.0.0.0')   </html>'''
```

### 方法二：使用jinja2模版，将代码包装起来



# http响应都包括什么？

一个典型的HTTP响应由以下几个部分组成：

1. 状态行（Status Line）：包括HTTP协议版本、状态码和相应的文本描述。例如：HTTP/1.1 200 OK。

2. 响应头（Response Headers）：包含有关响应的元数据信息，以键值对的形式表示。常见的响应头包括Content-Type、Content-Length、Cache-Control、Server等。响应头提供了关于响应内容和服务器的信息。

3. 空白行：位于状态行和响应体之间的空行，用于分隔响应头和响应体。

4. 响应体（Response Body）：包含实际的响应内容。响应体可以是HTML文档、JSON数据、图片、文件等。它的格式由Content-Type响应头指定。

```
以下是一个简单的示例HTTP响应的结构：
    HTTP/1.1 200 OK
    Content-Type: text/html
    Content-Length: 127

    <!DOCTYPE html>
    <html>
    <head>
        <title>Example</title>
    </head>
    <body>
        <h1>Hello, World!</h1>
    </body>
    </html>
```


