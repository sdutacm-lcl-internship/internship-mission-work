CREATE DATABASE IF NOT EXISTS cf;
USE cf;

CREATE TABLE user_info(
	handle VARCHAR(50) PRIMARY KEY NOT NULL,
	rating INT,
	`rank` VARCHAR(50),
	updated_at DATETIME NOT NULL
);

CREATE TABLE user_ratings(
	user_rating_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
	handle VARCHAR(50) NOT NULL,
	contest_id INT NOT NULL,
	contest_name VARCHAR(250) NOT NULL,
	`rank` VARCHAR(250) NOT NULL,
	old_rating INT NOT NULL,
	new_rating INT NOT NULL,
	rating_updated_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	FOREIGN KEY (handle) REFERENCES user_info(handle)
);



