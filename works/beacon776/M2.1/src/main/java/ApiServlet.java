import org.json.JSONArray;
import jakarta.servlet.*;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.*;
import org.json.JSONObject;
import java.io.*;

/* emmmmmm，以下内容在M2.1中没有起到任何作用，我在Main方法里就已经调用好了jdk自带的服务端。
先这样吧，我懒得管tomcat的配置了。
写的这些不想删了，就留着吧，反正暂时是没用上。*/

@WebServlet("/api")
public class ApiServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String handles = request.getParameter("handles");
        if(handles == null || handles.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            response.setContentType("application/json");
            response.getWriter().write(new JSONObject()
                    .put("success", false)
                    .put("type", 4)
                    .put("message", "Missing handles query parameter")
                    .toString());
            return;
        }

        JSONArray responseArray = UserService.getMultipleUserInformation(handles);


        response.setContentType("application/json");
        response.setStatus(HttpServletResponse.SC_OK);

        response.getWriter().write(responseArray.toString());
    }
}
