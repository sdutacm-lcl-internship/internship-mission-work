import org.json.JSONArray;
import org.json.JSONObject;
// 注意，import json的同时，也需要在maven中加入json依赖哦
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.IOException;
import java.util.Scanner;

public class Main {
    private static JSONObject getUserInformation(String handle) throws IOException {
        String apiUrl = "https://codeforces.com/api/user.info?handles=" + handle;// 调用 url
        HttpURLConnection connection = null;

        try {
            /* 创建一个 URL 对象,通过 URL 对象打开连接，得到 HttpURLConnection 对象,
            设置请求方法为 GET（可以是 POST、PUT 等）,设置连接超时和读取超时（毫秒）,
            获取响应码（200 表示成功）. 如果响应码是 200，读取响应数据
            注意connection那里不能写注释，要不会connect会读取注释的信息......
             */
            URL url = new URL(apiUrl);
            connection = (HttpURLConnection) url.openConnection();// url 转 HttpURLConnection
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(5000);

            // 处理响应的状态码
            int status = connection.getResponseCode();
            if(status != 200) {
                throw new IOException("disCorrect status = " + status);
            }

            // 读取响应内容，用缓冲流 + 字节流处理读入的数据
            /* 我们已知信息就是纯文本的形式，就直接用字节流没有问题的啦*/
            String line;
            StringBuilder result = new StringBuilder();
            BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
            while((line = in.readLine()) != null) {
                result.append(line);// append支持append一个String，StringBuilder不能直接与String相加
            }
            in.close();

            // 重头戏:解析 JSON 数据
            // 注意，虽然StringBuilder类看起来是没有改变字符串本身的，但是它返回的是String形式，我们需要String类型的参数才能转到JSONObject类型。
            JSONObject jsonResponse = new JSONObject(result.toString());
            // JSONObject的底层用HashMap维护的，键值是对应的，可以用get去查询key对应的value。
            if("OK".equals(jsonResponse.getString("status"))) {
                JSONArray jsonArray = jsonResponse.getJSONArray("result");
                if(!jsonArray.isEmpty()) {
                    return jsonArray.getJSONObject(0);
                } else {
                    return null;
                }
            } else {
                throw new IOException("API call failed:" + jsonResponse.toString());
            }
        } catch(IOException e) {
            // 注意，当handle不合法时，报错常为disCorrect status = 400 状态码为400时，表示发送的 HTTP 请求存在问题。如请求参数不合法、请求方法错误。所以handle不合法时会进行下面这个报错
            // 4开头的状态码都是Client Error 客户端错误状态码
            System.err.println("Error when fetching or phrasing data:" + e.getMessage());
            return null;
        } finally {
            if(connection != null) {
                connection.disconnect();// 去读了一下源码，disconnect()方法的作用是让这个HttpURLConnection实例不再被复用
            }
        }
    }

    private static void handleError(String errorMessage) {
        System.err.println(errorMessage);// 魔法书提过要用err输出报错
    }

    public static void main(String[] args) {
        // args就是arguments 参数的缩写，这就是我们传入的参数。
        /* 检查输入参数
         现在用string数组进行处理,能同时查询多个用户handle不唯一的情况啦，注意要给多个handle用空隔分割哦*/
        try (Scanner scanner = new Scanner(System.in)) {
            while (true) {
                System.out.println("Please input Codeforces handles or \"exit\" :");
                String line = scanner.nextLine();
                String[] handles = line.split(" ");
                if(line.equals("exit")) {
                    System.out.println("Exiting the programme.");
                    System.exit(0);
                }
                boolean thisLineHasError = false;

                for(String handle : handles) {
                    try {
                        //用StringBuilder一个个查询并添加是第二版方案。如果严格按照handle，rating，rank的顺序进行输出，以JSONObject的默认顺序不太行，因为它底层是用HashMap维护的，乱序。

                        StringBuilder output = new StringBuilder();
                        JSONObject information = getUserInformation(handle);

                        if (information != null) {
                            output.append("{");

                            output.append("\"handle\":\"").append(information.getString("handle")).append("\"");
                            // 查一下合法handle用户有没有rating，有rating就一定有rank
                            if (information.has("rating")) {
                                output.append(",\"rating\":\"").append(information.getInt("rating")).append("\"");
                                output.append(",\"rank\":\"").append(information.getString("rank")).append("\"");
                            }

                            output.append("}");

                            System.out.println(output);
                            // 这里不要求参数类型了，toString()无所谓了
                        } else {
                            // 根据上面的调用方法，如果handle不合法，information就是null，这里处理一下"no such handle"的报错就行。但是报错只能是红色的了，和py不一样，我没法控制.
                            // 先别着急退出，先把这一行处理完再考虑报错。
                            handleError("no such handle");
                            thisLineHasError = true;

                        }

                    } catch (IOException e) {
                        handleError("The Error is:" + e.getMessage());
                        // 先别着急退出，先把这一行处理完再考虑报错。
                        thisLineHasError = true;
                    }
                }
                // 把该行所有数据都处理完再去处理异常
                if(thisLineHasError) {
                    System.exit(1);
                }
            }
        }
    }

}

