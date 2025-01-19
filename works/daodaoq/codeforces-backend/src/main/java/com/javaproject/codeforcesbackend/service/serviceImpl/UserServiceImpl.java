package com.javaproject.codeforcesbackend.service.serviceImpl;

import com.javaproject.codeforcesbackend.mapper.UserMapper;
import com.javaproject.codeforcesbackend.pojo.Contest;
import com.javaproject.codeforcesbackend.pojo.User;
import com.javaproject.codeforcesbackend.service.UserService;
import com.javaproject.codeforcesbackend.utils.CodeforcesApiTool;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserMapper userMapper;

    private CodeforcesApiTool apiTool = new CodeforcesApiTool();

    @Override
    public List<User> query(List<String> usernames) {
        List<User> users = new ArrayList<>();
        for (String username : usernames) {
            User user = userMapper.findByHandle(username);
            if (user == null) {
                try {
                    user = apiTool.fetchUserInfo(username);
                    LocalDateTime now = LocalDateTime.now();
                    String formattedDateTime = now.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
                    userMapper.add(user.getHandle(), user.getRating(), user.getRank(), formattedDateTime);
                    user = userMapper.findByHandle(username); // 再次查询，确保插入的用户加入列表
                } catch (Exception e) {
                    System.err.println("Failed to fetch user info: " + e.getMessage());
                    continue; // 跳过失败的用户
                }
            }
            if (user != null) {
                users.add(user);
            }
        }
        return users;
    }

    @Override
    public List<Contest> find(List<String> usernames) {
        List<Contest> allContests = new ArrayList<>(); // 用于存储所有用户的比赛记录

        for (String username : usernames) {
            List<Contest> contests = userMapper.findContestsByHandle(username);

            if (contests == null || contests.isEmpty()) {
                try {
                    // 从 API 获取比赛数据
                    contests = apiTool.fetchUserContests(username);

                    // 将从 API 获取的比赛数据插入数据库
                    for (Contest contest : contests) {
                        LocalDateTime now = LocalDateTime.now();
                        String formattedDateTime = now.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
                        userMapper.addContest(
                                contest.getHandle(),
                                contest.getContestId(),
                                contest.getContestName(),
                                contest.getRank(),
                                contest.getRatingUpdatedAt(),
                                contest.getOldRating(),
                                contest.getNewRating(),
                                formattedDateTime // 传入当前时间作为 updated_at
                        );
                    }

                    // 再次从数据库查询，确保插入后获取最新数据
                    contests = userMapper.findContestsByHandle(username);

                } catch (Exception e) {
                    System.err.println("Failed to fetch or store contest data for user: " + username);
                    e.printStackTrace();
                    continue; // 跳过失败的用户，继续处理下一个用户
                }
            }

            // 将当前用户的比赛数据添加到最终结果集合中
            if (contests != null && !contests.isEmpty()) {
                allContests.addAll(contests);
            }
        }

        return allContests; // 返回包含所有用户比赛记录的列表
    }
}
