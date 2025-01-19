package com.javaproject.codeforcesbackend.pojo;

import lombok.Data;

import java.util.Date;

@Data
public class Contest {
    private String handle;
    private int contestId;
    private String contestName;
    private int rank;
    private Date ratingUpdatedAt;
    private int oldRating;
    private int newRating;

    public Contest(String handle, int contestId, String contestName, int rank, Date ratingUpdatedAt, int oldRating, int newRating) {
        this.handle = handle;
        this.contestId = contestId;
        this.contestName = contestName;
        this.rank = rank;
        this.ratingUpdatedAt = ratingUpdatedAt;
        this.oldRating = oldRating;
        this.newRating = newRating;
    }

    public Contest() {
    }
}
