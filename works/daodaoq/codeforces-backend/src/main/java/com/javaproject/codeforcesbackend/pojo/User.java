package com.javaproject.codeforcesbackend.pojo;

import lombok.Data;

import java.util.Date;

@Data
public class User {
    private String handle;
    private int rating;
    private String rank;

    public User(String handle, int rating, String rank) {
        this.handle = handle;
        this.rating = rating;
        this.rank = rank;
    }

    public User() {
    }

    @Override
    public String toString() {
        return String.format("User{handle='%s', rating=%d, rank='%s'}", handle, rating, rank);
    }
}
