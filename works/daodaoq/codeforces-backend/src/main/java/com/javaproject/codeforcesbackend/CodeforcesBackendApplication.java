package com.javaproject.codeforcesbackend;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.javaproject.codeforcesbackend.mapper")
public class CodeforcesBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(CodeforcesBackendApplication.class, args);
    }

}
