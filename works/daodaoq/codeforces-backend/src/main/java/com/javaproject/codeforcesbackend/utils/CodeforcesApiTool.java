package com.javaproject.codeforcesbackend.utils;

import com.javaproject.codeforcesbackend.pojo.Contest;
import com.javaproject.codeforcesbackend.pojo.User;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class CodeforcesApiTool {

    private static final String API_URL = "https://codeforces.com/api/user.info?handles=";

    /**
     * 从Codeforces API获取用户信息（单个用户名）。
     *
     * @param handle 用户名
     * @return 包含用户名、评级和排名的 User 对象
     * @throws Exception 如果 API 调用或 JSON 解析失败
     */
    public static User fetchUserInfo(String handle) throws Exception {
        // 使用用户名构建 API URL
        String urlString = API_URL + handle;

        // 创建 URI 和 URL 对象
        URI uri = URI.create(urlString);
        URL url = uri.toURL();

        // 创建与 URL 的连接
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");

        // 读取来自 API 的响应
        BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String inputLine;

        while ((inputLine = in.readLine()) != null) {
            response.append(inputLine);
        }
        in.close();

        // 解析 JSON 响应
        return parseUserJson(response.toString());
    }

    /**
     * 解析来自 Codeforces API 的 JSON 响应，以提取用户信息。
     *
     * @param jsonResponse JSON 字符串响应
     * @return User 对象
     */
    private static User parseUserJson(String jsonResponse) {
        JSONObject jsonObject = new JSONObject(jsonResponse);

        if (!"OK".equals(jsonObject.getString("status"))) {
            throw new IllegalStateException("API 响应状态不是 OK。");
        }

        JSONArray resultArray = jsonObject.getJSONArray("result");
        if (resultArray.isEmpty()) {
            throw new IllegalStateException("未找到该用户名的用户信息。");
        }

        JSONObject userObject = resultArray.getJSONObject(0);

        String handle = userObject.getString("handle");
        int rating = userObject.has("rating") ? userObject.getInt("rating") : -1;
        String rank = userObject.has("rank") ? userObject.getString("rank") : "unrated";

        return new User(handle, rating, rank);
    }

    private static final String API_URL_USER_RATING = "https://codeforces.com/api/user.rating?handle=";

    /**
     * 从 Codeforces API 获取用户的竞赛历史记录（单个用户名）。
     *
     * @param handle 用户名
     * @return 包含竞赛数据的 Contest 对象列表
     * @throws Exception 如果 API 调用或 JSON 解析失败
     */
    public static List<Contest> fetchUserContests(String handle) throws Exception {
        String urlString = API_URL_USER_RATING + handle;
//        String urlString = "https://codeforces.com/api/user.rating?handle=" + handle + "&count=50&offset=50";
        String jsonResponse = makeApiRequest(urlString);
        return parseContestJson(jsonResponse, handle);
    }

    /**
     * 通用方法，用于发起 API 请求并返回响应字符串。
     *
     * @param urlString API URL
     * @return API 响应字符串
     * @throws Exception 如果连接失败
     */
    private static String makeApiRequest(String urlString) throws Exception {
        URI uri = URI.create(urlString);
        URL url = uri.toURL();
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");

        BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
        StringBuilder response = new StringBuilder();
        String inputLine;

        while ((inputLine = in.readLine()) != null) {
            response.append(inputLine);
        }
        in.close();
        return response.toString();
    }

    /**
     * 解析来自 Codeforces API 的 JSON 响应，以提取竞赛历史。
     *
     * @param jsonResponse JSON 字符串响应
     * @param handle 用户名
     * @return Contest 对象列表
     */
    private static List<Contest> parseContestJson(String jsonResponse, String handle) {
        JSONObject jsonObject = new JSONObject(jsonResponse);

        if (!"OK".equals(jsonObject.getString("status"))) {
            throw new IllegalStateException("API 响应状态不是 OK。");
        }

        JSONArray resultArray = jsonObject.getJSONArray("result");
        List<Contest> contests = new ArrayList<>();

        for (int i = 0; i < resultArray.length(); i++) {
            JSONObject contestObject = resultArray.getJSONObject(i);

            int contestId = contestObject.getInt("contestId");
            String contestName = contestObject.getString("contestName");
            int rank = contestObject.getInt("rank");
            int oldRating = contestObject.getInt("oldRating");
            int newRating = contestObject.getInt("newRating");
            long ratingUpdateTimeSeconds = contestObject.getLong("ratingUpdateTimeSeconds");

            // 将时间戳转换为 Date 对象
            Date ratingUpdatedAt = new Date(ratingUpdateTimeSeconds * 1000);

            contests.add(new Contest(handle, contestId, contestName, rank, ratingUpdatedAt, oldRating, newRating));
        }
        return contests;
    }
}
