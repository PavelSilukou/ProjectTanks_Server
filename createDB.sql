DROP TABLE IF EXISTS Map;

CREATE TABLE Map
(
	MapName CHAR(20) PRIMARY KEY,
	Height INT NOT NULL,
	Width INT NOT NULL,
	Obstacles TEXT NOT NULL
);