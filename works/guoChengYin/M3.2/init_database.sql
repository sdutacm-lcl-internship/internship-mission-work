-- init_database.sql
--该文件在项目每次启动时读取，由其初始化数据库cf.db。所有的语句都是若已存在则不进行操作，若无则新建。



-- 开启外键支持
PRAGMA foreign_keys = ON;

-- 建立 user_info 表
CREATE TABLE IF NOT EXISTS user_info (
    handle VARCHAR PRIMARY KEY NOT NULL,
    rating INT,
    rank VARCHAR,
    updated_at DATETIME NOT NULL
);

-- 建立 user_rating 表
CREATE TABLE IF NOT EXISTS user_rating (
    user_rating_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    handle VARCHAR NOT NULL,
    contest_id INT NOT NULL,
    contest_name VARCHAR NOT NULL,
    rank INT NOT NULL,
    old_rating INT NOT NULL,
    new_rating INT NOT NULL,
    rating_updated_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (handle) REFERENCES user_info (handle) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 在user_rating表上建立一个索引
-- 创建唯一索引，确保handle和contest_id组合的唯一性
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_handle_contest ON user_rating (handle, contest_id);
