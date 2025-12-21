
--
-- Database: `tts` FOR SQLITE 3 
--

-- --------------------------------------------------------

--
-- Table structure for table `faculty`
--

CREATE TABLE `faculty` (
  `acronym` varchar(10) PRIMARY KEY ,
  `name` text,
  `last_updated` datetime NOT NULL
);

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
);

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
  `last_updated` datetime NOT NULL,
  `hash` varchar(64) ,
  UNIQUE (`id`, `semester`, `year`)
  FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

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
  FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
);


CREATE TABLE `info` (
  `date` DATETIME PRIMARY KEY
);

-- --------------------------------------------------------
--
-- Table for `course group`
--
CREATE TABLE `course_group` (
  `id` INTEGER PRIMARY KEY,
  `name` varchar(64),
  `course_id` INTEGER NOT NULL,
  `year` INTEGER NOT NULL,
  `semester` INTEGER NOT NULL,
  FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

-- --------------------------------------------------------
--
-- Table for `course_unit_course_group`
--
CREATE TABLE `course_unit_course_group` (
  `course_unit_id` INTEGER NOT NULL,
  `course_group_id` INTEGER NOT NULL,
  PRIMARY KEY (`course_unit_id`, `course_group_id`),
  FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`course_group_id`) REFERENCES `course_group`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

