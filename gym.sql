CREATE DATABASE gym_db;
USE gym_db;

CREATE TABLE info(username VARCHAR(200), password VARCHAR(500), name VARCHAR(100), prof INT, street VARCHAR(100), city VARCHAR(50), phone VARCHAR(32), time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(username));

CREATE TABLE plans(name VARCHAR(100), PRIMARY KEY(name));

CREATE TABLE receps(username VARCHAR(200), PRIMARY KEY(username), FOREIGN KEY(username) references info(username));

CREATE TABLE trainors(username VARCHAR(200), PRIMARY KEY(username), FOREIGN KEY(username) references info(username));

CREATE TABLE members(username VARCHAR(200), plan VARCHAR(100), trainor VARCHAR(200), PRIMARY KEY(username), FOREIGN KEY(username) references info(username), FOREIGN KEY(plan) references plans(name), FOREIGN KEY(trainor) references trainors(username));

CREATE TABLE progress(username VARCHAR(200), date DATE, daily_result VARCHAR(200), time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(username, date), FOREIGN KEY(username) references members(username));

CREATE TABLE equip(name VARCHAR(200), count INT,PRIMARY KEY(name));

INSERT INTO info(username, password, name, profile, street, city, phone) VALUES('brunadamaris', '$5$rounds=535000$CUiEsvrYrO/d.JfC$2p44wvE.pdj7TGhHWJE3XUM2lGz/5Y57BtFuqF4bJ23', 'Bruna Ramos', 1, 'A', 'B', 123456789); -- password: admin1

SELECT * FROM info;
SELECT * FROM equip;
SELECT * FROM receps;
SELECT * FROM progress;
SELECT * FROM members;
SELECT * FROM trainors;
SELECT * FROM plans;

