CREATE TABLE IF NOT EXISTS `ToDoData` (
  `item` varchar(255) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `start` date DEFAULT NULL,
  `due` date DEFAULT NULL,
  `complete` date DEFAULT NULL,
  PRIMARY KEY (`item`)
);