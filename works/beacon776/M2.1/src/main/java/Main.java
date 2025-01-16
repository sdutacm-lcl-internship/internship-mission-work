import org.json.JSONObject;
import org.json.JSONArray;

// 注意，import json的同时，也需要在maven中加入json依赖哦
import java.io.*;
import java.net.InetSocketAddress;
import com.sun.net.httpserver.*;

public class Main {

    public static void main(String[] args) throws IOException {
        // 用jdk自带的Http服务器，监听127.0.0.1:2333
        HttpServer server = HttpServer.create(new InetSocketAddress(2333), 0);

        // "/"是指定HTTP请求的路径上下文，表示服务器会处理所有以/开头的请求
        /* 即使用 server.createContext("/", new ApiHandler()); 时，
        所有访问根路径的请求都会交给 ApiHandler 处理。*/

        server.createContext("/", new ApiHandler());
        server.start();
        System.out.println("Server started at http://127.0.0.1:2333/");
    }
    static class ApiHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String query = exchange.getRequestURI().getQuery();
            String handles = null;
            if(query != null && query.startsWith("handles=")) {
                handles = query.substring(8);// 因为query的开头是handles= 它占了7个位置，所以我们把前七个位置让出来
            }

            if(handles == null) {
                // 直接调用下面那个方法处理运行时异常的输出
                sendErrorResponse(exchange, 400, "Missing handles query parameter");
                return;
            }

            // 调用UserService里的方法，先把多组handles获得的结果分割成JSONObject数组
            JSONArray responseArray = UserService.getMultipleUserInformation(handles);

            // 设置响应头，返回json类型
            exchange.getResponseHeaders().set("Content-Type", "application/json");

            // 响应内容
            byte[] responseBytes = responseArray.toString().getBytes("UTF-8");

            // 设置响应码
            exchange.sendResponseHeaders(200, responseBytes.length);

            OutputStream os = exchange.getResponseBody();
            os.write(responseBytes); // 写入响应主体
            os.close();
        }
    }

    private static void sendErrorResponse(HttpExchange exchange, int statusCode, String message) throws IOException {
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        String response = new JSONObject()
                .put("success", false)
                .put("type", 4)
                .put("message", message)
                .toString();
        byte[] responseBytes = response.getBytes();
        exchange.sendResponseHeaders(statusCode, responseBytes.length);
        OutputStream os = exchange.getResponseBody();
        os.write(responseBytes);
        os.close();

    }
}






