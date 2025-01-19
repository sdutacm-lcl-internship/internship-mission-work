# 基础镜像
FROM eclipse-temurin:21
# 作者
MAINTAINER xp
# 工作目录
WORKDIR /usr/local/java
# 同步docker内部的时间
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
# 设置时区
ENV TZ=Asia/Shanghai
EXPOSE 9898
# 复制jar包到/user/local/java下
ARG JAR_FILE
ADD ${JAR_FILE} ./bili.jar

ENTRYPOINT ["nohup","java","-Dspring.profiles.active=online","-Dspring.config.location=/usr/local/java/application.yml,/usr/local/java/application-online.yml","-jar","/usr/local/java/bili.jar",">","/usr/local/java/bili.log","&>","&"]