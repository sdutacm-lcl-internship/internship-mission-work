package com.javaproject.codeforcesbackend.mapper;

import com.javaproject.codeforcesbackend.pojo.Contest;
import com.javaproject.codeforcesbackend.pojo.User;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.Date;
import java.util.List;

@Mapper
public interface UserMapper {

    @Select("select * from `data-user-info` where handle = #{username}")
    User findByHandle(String username);

    @Select("select * from `data-user-rating` where handle = #{handle}")
    List<Contest> findContestsByHandle(@Param("handle") String handle);

    @Insert("insert into `data-user-info`(handle, rating, `rank`, updated_at) " +
            "values (#{handle}, #{rating}, #{rank}, #{updatedAt})")
    void add(String handle, int rating, String rank, String updatedAt);

    @Insert("insert into `data-user-rating` (handle, contest_id, contest_name, `rank`, rating_updated_at, old_rating, new_rating, updated_at) " +
            "values (#{handle}, #{contestId}, #{contestName}, #{rank}, #{ratingUpdatedAt}, #{oldRating}, #{newRating}, #{updatedAt})")
    void addContest(String handle, int contestId, String contestName, int rank, Date ratingUpdatedAt, int oldRating, int newRating, String updatedAt);
}
