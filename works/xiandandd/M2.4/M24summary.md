# 常见的请求体类型

以下是常见的请求体类型：

1. `application/json`: 用于发送 JSON 数据的请求体。数据被序列化为 JSON 格式，并通过请求体传递。

2. `application/x-www-form-urlencoded`: 用于发送表单数据的请求体。数据以键值对的形式通过请求体传递，每个键值对之间用 `&` 符号分隔。

3. `multipart/form-data`: 用于上传文件或同时发送多种类型数据的请求体。数据以多部分形式组织，并通过请求体进行传递。

4. `text/plain`: 用于发送纯文本数据的请求体。数据以纯文本形式通过请求体进行传递。

5. `application/xml`: 用于发送 XML 数据的请求体。数据以 XML 格式进行组织，并通过请求体进行传递。

当发送请求时，可以根据需要选择适当的请求体类型，并设置请求头中的 `Content-Type` 字段来指示服务器如何解析请求体的内容。服务器端根据 `Content-Type` 来解析对应请求体的数据。

# 测试工具-postman

可以很方便的测试post和get请求方式，自定义请求体

要传送json数据的话，要在raw模块中，选择json格式

# 多重字典（`MultiDict`）

```python
MultiDict([('cacheType', '"userInfo"'), ('handles', '["jiangly"]')])
```

`MultiDict` 是一个键值对的集合，它允许一个键对应多个值，这与普通的字典（`dict`）不同。在这个例子中，有两个键值对：`cacheType` 对应的值是 `"userInfo"`，`handles` 对应的值是 `["jiangly"]`，该值是一个包含一个字符串元素 `"jiangly"` 的列表。

```python
要访问`MultiDict`中的内容，你可以使用字典的方式访问其中的键值对。以下是一个示例代码片段，展示如何访问`MultiDict`中的内容：
    data = MultiDict([('cacheType', '"userInfo"'), ('handles', '["jiangly"]')])

    # 访问键值对
    cache_type = data['cacheType']
    handles = data['handles']

    print(cache_type)  # 输出: "userInfo"
    print(handles)  # 输出: '["jiangly"]'
```

```python
你也可以使用`.get()`方法来访问`MultiDict`中的内容。这种方法可以指定一个默认值，在键不存在时返回该默认值。
    data = MultiDict([('cacheType', '"userInfo"'), ('handles', '["jiangly"]')])

    # 使用.get()方法访问键值对
    cache_type = data.get('cacheType')
    handles = data.get('handles')

    print(cache_type)  # 输出: "userInfo"
    print(handles)  # 输出: '["jiangly"]'
```

# 关于x-www-form-urlencoded格式

`x-www-form-urlencoded` 是一种常见的数据编码格式，通常用于在 HTTP 请求中传输表单数据。它主要是通过将表单字段的名称和值编码为键值对，并使用特定的字符进行分隔，然后将编码后的数据作为请求的一部分发送到服务器。

在 `x-www-form-urlencoded` 格式中，各个键值对由 `&` 符号分隔，而键和值之间则使用 `=` 符号分隔。对于特殊字符和非ASCII字符，会使用百分号编码（URL 编码）进行表示。

```python
以下是示例数据使用 `x-www-form-urlencoded` 格式的表现形式：
    name=John+Doe&age=25&city=London
```

在这个例子中，有三个键值对：`name` 对应的值是 `John Doe`，`age` 对应的值是 `25`，`city` 对应的值是 `London`。

`x-www-form-urlencoded` 格式常用于 HTML 表单提交、AJAX 请求和 API 请求中。在服务器端接收到这种格式的数据后，可以通过解析数据来获取各个字段的值，用于后续的处理。

# flask怎么解析 application/x-www-form-urlencoded这种请求中的参数值

在 Flask 中，你可以使用 `request.form`（或 `request.values`）来解析 `application/x-www-form-urlencoded` 格式的请求参数值。

`request.form` 是一个字典对象，包含了所有通过 POST 方法提交的表单数据。它会自动解析 `application/x-www-form-urlencoded` 格式的请求体，并将每个表单字段的值映射到相应的键。

```python
以下是一个示例展示如何在 Flask 中解析 `application/x-www-form-urlencoded` 格式的请求参数值：
    from flask import Flask, request

    app = Flask(__name__)

    @app.route('/process_form', methods=['POST'])
    def process_form():
        # 获取表单字段的值
        name = request.form['name']
        age = request.form['age']
        city = request.form['city']

        # 处理数据...
        # ...

        return 'Form submitted successfully'

    if __name__ == '__main__':
        app.run()
```

在这个例子中，我们定义了一个 `process_form` 路由，它接收一个 `POST` 请求，并从请求的表单中获取 `name`、`age` 和 `city` 字段的值。你可以根据你的实际需求访问其他表单字段。

要注意的是，为了使用 `request.form` 解析表单数据，你首先需要确保你的视图函数装饰器中指定了 `methods=['POST']`，以仅接受 `POST` 请求。

另外，你还可以使用 `request.values` 来获取所有的请求参数（无论是通过 `GET` 还是 `POST` 提交的），这可以更加灵活地处理不同类型的请求。

# 在HTTP中，常见的请求传递方式（重要）

* URL参数传递（Query Parameters）：参数通过URL的查询字符串（query string）传递，通过`?`符号和`&`符号连接参数名和值。例如：`http://example.com/search?keyword=hello&page=1`。在服务端，可以使用`request.args.get('keyword')`来获取参数值。

* 请求体传递（Request Body）：请求数据作为请求体的一部分，通常使用POST、PUT、PATCH等请求方法。请求体可以使用不同的数据格式，如表单数据（`application/x-www-form-urlencoded`）、JSON数据（`application/json`）、多媒体数据（`multipart/form-data`）等。在服务端，可以使用框架提供的方法如`request.form`或`request.json`来获取请求体中的数据。

* 路径参数传递（Path Parameters）：参数通过URL的路径中的特定位置进行传递。例如：`http://example.com/users/123`，其中`123`是用户ID参数。在服务端，可以使用框架提供的路由配置，使用特定的占位符来捕获参数值。

* 请求头传递（Request Headers）：参数通过HTTP请求头部的字段进行传递。请求头部包含键值对，为了传递参数，可以在请求头中添加自定义字段。例如：`X-API-Token: 12345`。在服务端，可以使用`request.headers.get('X-API-Token')`来获取请求头部字段的值。
