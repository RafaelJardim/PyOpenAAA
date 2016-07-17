CREATE DATABASE IF NOT EXISTS `tacacs`;

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

USE `tacacs`;

--
-- Table structure for table `access`
--

DROP TABLE IF EXISTS `access`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `access` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tty` varchar(10) COLLATE utf8_bin DEFAULT NULL,
  `start_stop` varchar(10) COLLATE utf8_bin DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `device_ip` varchar(15) CHARACTER SET utf8 DEFAULT NULL,
  `username` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `server_ip` varchar(15) CHARACTER SET utf8 DEFAULT NULL,
  `service` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `timezone` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `task_id` int(11) DEFAULT NULL,
  `disc-cause` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `stop_time` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `elapsed_time` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `pre-session-time` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `disc-cause-ext` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='	';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `account`
--

DROP TABLE IF EXISTS `account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tty` varchar(10) COLLATE utf8_bin DEFAULT NULL,
  `start_stop` varchar(10) COLLATE utf8_bin DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `device_ip` varchar(15) CHARACTER SET utf8 DEFAULT NULL,
  `username` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `server_ip` varchar(15) CHARACTER SET utf8 DEFAULT NULL,
  `service` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `timezone` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `task_id` int(11) DEFAULT NULL,
  `priv_lvl` int(2) DEFAULT NULL,
  `cmd` varchar(100) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='	';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cmd_sets`
--

DROP TABLE IF EXISTS `cmd_sets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cmd_sets` (
  `cmd_set_id` int(11) NOT NULL AUTO_INCREMENT,
  `cmd_set_name` varchar(45) CHARACTER SET utf8 NOT NULL,
  `cmd_default_action` varchar(45) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`cmd_set_id`),
  UNIQUE KEY `cmd_set_id_UNIQUE` (`cmd_set_id`),
  UNIQUE KEY `cmd_set_name_UNIQUE` (`cmd_set_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cmd_sets`
--

LOCK TABLES `cmd_sets` WRITE;
/*!40000 ALTER TABLE `cmd_sets` DISABLE KEYS */;
INSERT INTO `cmd_sets` VALUES (1,'permit_all','permit'),(2,'show_only','deny');
/*!40000 ALTER TABLE `cmd_sets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cmds`
--

DROP TABLE IF EXISTS `cmds`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cmds` (
  `cmd_id` int(11) NOT NULL AUTO_INCREMENT,
  `cmd_set_id` int(11) NOT NULL,
  `cmd_order` int(11) NOT NULL,
  `action` varchar(10) COLLATE utf8_bin NOT NULL,
  `cmd` varchar(100) COLLATE utf8_bin NOT NULL,
  `parameter` varchar(100) COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`cmd_id`),
  UNIQUE KEY `cmd_id_UNIQUE` (`cmd_id`),
  KEY `fk_cmds_cmd_set_id` (`cmd_set_id`),
  CONSTRAINT `fk_cmds_cmd_set_id` FOREIGN KEY (`cmd_set_id`) REFERENCES `cmd_sets` (`cmd_set_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cmds`
--

LOCK TABLES `cmds` WRITE;
/*!40000 ALTER TABLE `cmds` DISABLE KEYS */;
INSERT INTO `cmds` VALUES (1,1,1,'permit','.*','.*'),(2,2,1,'permit','show','.*'),(3,2,2,'permit','exit','.*');
/*!40000 ALTER TABLE `cmds` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `group_id` int(11) NOT NULL AUTO_INCREMENT,
  `group_name` varchar(45) CHARACTER SET utf8 NOT NULL,
  `cmd_set_id` int(11) NOT NULL,
  `priv_lvl` int(11) NOT NULL,
  `idle_time` int(11) NOT NULL,
  `timeout` int(11) NOT NULL,
  PRIMARY KEY (`group_id`),
  UNIQUE KEY `group_UNIQUE` (`group_name`),
  KEY `cmd_set_id_idx` (`cmd_set_id`),
  CONSTRAINT `fk_groups_cmd_set_id` FOREIGN KEY (`cmd_set_id`) REFERENCES `cmd_sets` (`cmd_set_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (1,'admin',1,15,30,60),(2,'operator',2,15,15,30);
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `settings` (
  `shared_key` varchar(45) COLLATE utf8_bin NOT NULL,
  `login_msg` varchar(255) COLLATE utf8_bin NOT NULL,
  `fail_msg` varchar(255) COLLATE utf8_bin NOT NULL,
  `time_zone` varchar(45) COLLATE utf8_bin NOT NULL,
  `custom_config` longtext COLLATE utf8_bin NOT NULL,
  PRIMARY KEY (`shared_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
INSERT INTO `settings` VALUES ('pyopenaaa','This Device is Managed by PyOpenAAA. Please inform your credentials:\\n','Authentication Failed.','UTC-0','');
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(45) CHARACTER SET utf8 NOT NULL,
  `passwd` varchar(45) CHARACTER SET utf8 NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username_UNIQUE` (`user_name`),
  KEY `group_id_idx` (`group_id`),
  CONSTRAINT `fk_users_group_id` FOREIGN KEY (`group_id`) REFERENCES `groups` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','$1$PyOpenAA$1Yy59TbXrsAH8Y0AmrfLk/',1),(2,'operator','$1$PyOpenAA$PPIVpm9mwOA1NA8kY1mev.',2);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;