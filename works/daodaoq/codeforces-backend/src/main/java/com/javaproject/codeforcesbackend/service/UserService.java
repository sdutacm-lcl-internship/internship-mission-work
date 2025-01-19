package com.javaproject.codeforcesbackend.service;

import com.javaproject.codeforcesbackend.pojo.Contest;
import com.javaproject.codeforcesbackend.pojo.User;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public interface UserService {
    List<User> query(List<String> usernames);

    List<Contest> find(List<String> usernames);
}
