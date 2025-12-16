-- phpMyAdmin SQL Dump
-- version 4.7.7


SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Database: `tts`
--


CREATE TABLE `faculty` (
  `acronym` varchar(10) PRIMARY KEY ,
  `name` text,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;


-- --------------------------------------------------------

--
-- Table structure for table `course`
--

CREATE TABLE `course` (
  `id` INTEGER PRIMARY KEY,
  `faculty_id` varchar(10) NOT NULL,
  `name` varchar(200) NOT NULL,
  `acronym` varchar(10) NOT NULL,
  `course_type` varchar(2) NOT NULL,
  `year` int(11) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `plan_url` varchar(2000) NOT NULL,
  `last_updated` datetime NOT NULL,
  FOREIGN KEY (`faculty_id`) REFERENCES `faculty`(`acronym`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;


-- --------------------------------------------------------

--
-- Table structure for table `course_unit`
--

CREATE TABLE `course_unit` (
  `id` INTEGER PRIMARY KEY,
  `course_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `acronym` varchar(16) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `semester` tinyint(4) NOT NULL,
  `year` smallint(6) NOT NULL,
  `schedule_url` varchar(2000) DEFAULT NULL,
  `hash` varchar(64),
  `last_updated` datetime NOT NULL,
  FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `course_metadata`
--

CREATE TABLE `course_metadata` (
  `course_id` int(11) NOT NULL,
  `course_unit_id` int(11) NOT NULL,
  `course_unit_year` tinyint(4) NOT NULL,
  `ects` float(4) NOT NULL,
  PRIMARY KEY (`course_id`, `course_unit_id`, `course_unit_year`),
  FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;

--
-- Table structure for table `info`
--

CREATE TABLE `info` (
  `date` DATETIME PRIMARY KEY
) ENGINE=InnoDB CHARSET = utf8 COLLATE = utf8_general_ci;

-- --------------------------------------------------------
--
-- Table for `course group`
--
CREATE TABLE `course_group` (
  `id` INTEGER PRIMARY KEY,
  `name` varchar(64),
  `course_id` INTEGER,
  `group_course_id` INTEGER,
  FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
);


-----------------------------------------------------------
--
-- Table for association of   course unit and course group

CREATE TABLE `course_unit_course_group` (
  `course_unit_id` INTEGER NOT NULL,
  `course_group_id` INTEGER NOT NULL,
  PRIMARY KEY (`course_unit_id`, `course_group_id`),
  FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`course_group_id`) REFERENCES `course_group`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
);


--
-- Indexes for table `course`
--
CREATE UNIQUE INDEX `course_course_id` ON `course` (`id`,`faculty_id`,`year`);
CREATE INDEX `course_faculty_acronym` ON `course` (`faculty_id`); 

--
-- Indexes for table `course_unit`
--
CREATE UNIQUE INDEX `course_unit_uniqueness` ON `course_unit`  (`id`,`course_id`,`year`,`semester`); 
CREATE INDEX `course_unit_course_id` ON `course_unit` (`course_id`);

--
-- Indexes for table `course_metadata`
-- 
CREATE INDEX `course_metadata_index` ON `course_metadata` (`course_id`, `course_unit_id`, `course_unit_year`); 
