package com.javaproject.codeforcesbackend.controller;

import com.javaproject.codeforcesbackend.pojo.Contest;
import com.javaproject.codeforcesbackend.pojo.Result;
import com.javaproject.codeforcesbackend.pojo.User;
import com.javaproject.codeforcesbackend.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private UserService userService;

    @PostMapping("/batchGetUserInfo")
    public Result query(@RequestBody List<String> usernames) {
        final List<User> users = userService.query(usernames);
        return Result.success(users);
    }

    @PostMapping("/getUserRatings")
    public Result find(@RequestBody List<String> usernames) {
        final List<Contest> contests = userService.find(usernames);
        return Result.success(contests);
    }
}
