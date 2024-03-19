
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


-- --------------------------------------------------------
--
-- Table structure for table `class`
--

CREATE TABLE `class` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `name` varchar(31) NOT NULL,
  `course_unit_id` int(11) NOT NULL,
  `last_updated` datetime NOT NULL,
  UNIQUE (`name`, `course_unit_id`)
  FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

-- --------------------------------------------------------
--
-- Table structure for table `slot`
--

CREATE TABLE `slot` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `lesson_type` varchar(3) NOT NULL,
  `day` tinyint(3) NOT NULL,
  `start_time` decimal(3,1) NOT NULL,
  `duration` decimal(3,1) NOT NULL,
  `location` varchar(31) NOT NULL,
  `is_composed` boolean NOT NULL,
  `professor_id` int (11),
  `class_id` int(11) NOT NULL,
  `last_updated` datetime NOT NULL,
  FOREIGN KEY (`class_id`) REFERENCES `class` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

-- -------------------------------------------------------- 
--
-- Table structure for table `class_professor`
--

CREATE TABLE `slot_professor` (
  `slot_id` INTEGER NOT NULL,
  `professor_id` INTEGER NOT NULL,
  FOREIGN KEY (`slot_id`) REFERENCES `slot` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`professor_id`) REFERENCES `professor` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY (`slot_id`, `professor_id`)
);

-- -------------------------------------------------------- 
--
-- Table structure for table `professor`
--

CREATE TABLE `professor` (
  `id` INTEGER PRIMARY KEY,
  `professor_acronym` varchar(16),
  `professor_name` varchar(100)
);

-- --------------------------------------------------------
--
-- Table structure for table `info`
--

CREATE TABLE `info` (
  `date` DATETIME PRIMARY KEY
);

-- --------------------------------------------------------