import org.json.JSONArray;
import org.json.JSONObject;
// 注意，import json的同时，也需要在maven中加入json依赖哦
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.io.IOException;

public class UserService {
    public static JSONObject getUserInformation(String handle) throws IOException {
        // 用UTF-8维护 中文 or 空格的查询(虽然cf的handle应该没有这种东西，但是如果真的有人这么输入的话还是得处理一下)
        String encodedHandle = URLEncoder.encode(handle, "UTF-8");
        String apiUrl = "https://codeforces.com/api/user.info?handles=" + encodedHandle;// 调用 url
        HttpURLConnection connection = null;

        try {
            // 注意connection那里不能写注释，要不会connection会读取注释的信息......
            URL url = new URL(apiUrl);
            connection = (HttpURLConnection) url.openConnection();// url 转 HttpURLConnection
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(5000);

            // 处理响应的状态码
            int status = connection.getResponseCode();
            if(status != HttpURLConnection.HTTP_OK) {
                throw new IOException("HTTP response with code " + status);
            }

            // 读取响应内容，用缓冲流 + 字节流处理读入的数据
            /* 我们已知信息就是纯文本的形式，就直接用字节流没有问题的啦*/
            StringBuilder result = new StringBuilder();
            // 新添加了 try-with-resources 形式的写法
            try(BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()))) {
                String line;
                while ((line = in.readLine()) != null) {
                    result.append(line);// append支持append一个String，StringBuilder不能直接与String相加
                }
            }

            // 重头戏:解析 JSON 数据
            // 注意，虽然StringBuilder类看起来是没有改变字符串本身的，但是它返回的是String形式，我们需要String类型的参数才能转到JSONObject类型。
            JSONObject jsonResponse = new JSONObject(result.toString());
            JSONObject data = new JSONObject();
            // JSONObject的底层用HashMap维护的，键值是对应的，可以用get去查询key对应的value。
            if("OK".equals(jsonResponse.getString("status"))) {
                JSONArray jsonArray = jsonResponse.getJSONArray("result");
                if(!jsonArray.isEmpty()) { // 情况1:handle可以正常找到
                    JSONObject temp = jsonArray.getJSONObject(0);
                    data.put("success", true)
                            .put("handle", handle);

                    if(temp.has("rating")) { // 情况1.2:存在rating和rank
                        data.put("rating", temp.getInt("rating"))
                                .put("rank", temp.getString("rank"));
                    }
                    return data;
                } else { // 情况2:handle无法找到
                    return new JSONObject()
                            .put("success", false)
                            .put("type", 1)
                            .put("message", "no such handle");
                }
            } else { //情况4:在查询此项时未收到有效 HTTP 响应
                return new JSONObject()
                        .put("success", false)
                        .put("type", 3)
                        .put("message", jsonResponse.toString());
            }
        } catch(IOException e) {
            // 情况3:在查询此项时遭遇异常 HTTP 响应
            JSONObject errorData = new JSONObject();
            errorData.put("success", false)
                    .put("type", 2)
                    .put("message", e.getMessage())
                    .put("details", new JSONObject().put("status", 503));
            // HTTP状态码 503是服务器无法处理请求时返回的一般错误响应
            return errorData;
        } finally {
            if(connection != null) {
                connection.disconnect();// 去读了一下源码，disconnect()方法的作用是让这个HttpURLConnection实例不再被复用
            }
        }
    }
    // 调用上面的那个处理单个handle的方法，我们可以返回多个handle对应的json数据
    public static JSONArray getMultipleUserInformation(String handles) {
        JSONArray resultArray = new JSONArray();
        String[] handlesArray = handles.split(",");

        for(String handle : handlesArray) {
            try {
                JSONObject result = getUserInformation(handle);
                resultArray.put(result);
            } catch (IOException e) {
                // 情况 3：在查询此项时遭遇异常 HTTP 响应
                JSONObject errorData = new JSONObject()
                        .put("success", false)
                        .put("type", 2)
                        .put("message", "HTTP response with code 503")
                        .put("details", new JSONObject().put("status", 503));
                resultArray.put(errorData);
            } catch(Exception e) { // 情况 5：在查询此项时程序发生运行时异常
                JSONObject errorData = new JSONObject()
                        .put("success", false)
                        .put("type", 4)
                        .put("message", "Internal Server Error");
                resultArray.put(errorData);
            }
        }
        return resultArray;
    }
}
