DROP DATABASE if exists db_plp;

CREATE DATABASE db_plp;
USE db_plp;

CREATE TABLE tbl_player
(
	openid VARCHAR(28) NOT NULL PRIMARY KEY,
	data BLOB NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT="用户表";

CREATE TABLE tbl_game
(
	game_name VARCHAR(20) NOT NULL PRIMARY KEY,
	data LONGBLOB NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT="玩法表";

CREATE TABLE tbl_plp
(
	plpid INT NOT NULL PRIMARY KEY,
	data LONGBLOB NOT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT="漂流瓶表";