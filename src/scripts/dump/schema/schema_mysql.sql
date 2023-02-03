
--
-- Database: `tts` FOR SQLITE 3 
--



-- --------------------------------------------------------

--
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
CREATE TABLE `faculty` (
  `acronym` varchar(255)(10) PRIMARY KEY ,
  `name` text,
  `last_updated` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------
--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
CREATE TABLE `course` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `faculty_acronym` varchar(255)(10) NOT NULL, 
  `course_id` int(11) NOT NULL,
  `name` varchar(255)(200) NOT NULL,
  `acronym` varchar(255)(10) NOT NULL,
  `course_type` varchar(255)(2) NOT NULL,
  `year` int(11) NOT NULL,
  `url` varchar(255)(2000) NOT NULL,
  `plan_url` varchar(255)(2000) NOT NULL,
  `last_updated` datetime NOT NULL,
  FOREIGN KEY (`faculty_acronym`) REFERENCES `faculty`(`acronym`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;;

-- --------------------------------------------------------

--
-- Table structure for table `course_unit`
--

DROP TABLE IF EXISTS `course_unit`;
CREATE TABLE `course_unit` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `course_unit_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `name` varchar(255)(200) NOT NULL,
  `acronym` varchar(255)(16) NOT NULL,
  `url` varchar(255)(2000) NOT NULL,
  `course_year` tinyint(4) NOT NULL,
  `semester` tinyint(4) NOT NULL,
  `year` smallint(6) NOT NULL,
  `schedule_url` varchar(255)(2000) DEFAULT NULL,
  `last_updated` datetime NOT NULL,
  FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- --------------------------------------------------------

--
-- Table structure for table `course_unit_year`
--

DROP TABLE IF EXISTS `course_unit_year`;
CREATE TABLE `course_unit_year` (
  `course_id` INTEGER NOT NULL,
  `course_unit_id` int(11) NOT NULL,
  `course_unit_year` tinyint(4) NOT NULL,
  PRIMARY KEY (`course_id`, `course_unit_id`, `course_unit_year`),
  FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
  FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;



-- --------------------------------------------------------

--
-- Table structure for table `schedule`
--

DROP TABLE IF EXISTS `schedule`;
CREATE TABLE `schedule` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `day` tinyint(3) NOT NULL,
  `duration` decimal(3,1) NOT NULL,
  `start_time` decimal(3,1) NOT NULL,
  `location` varchar(255)(31) NOT NULL,
  `lesson_type` varchar(255)(3) NOT NULL,
  `teacher_acronym` varchar(255)(16) NOT NULL,
  `course_unit_id` int(11) NOT NULL,
  `last_updated` datetime NOT NULL,
  `class_name` varchar(255)(31) NOT NULL,
  `composed_class_name` varchar(255)(16) DEFAULT NULL,
  FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;;

-- -------------------------------------------------------- 

--
-- Indexes for dumped tables
--

--
-- Indexes for table `course`
--
CREATE UNIQUE INDEX `course_course_id` ON `course` (`course_id`,`faculty_acronym`,`year`);
CREATE INDEX `course_faculty_acronym` ON `course` (`faculty_acronym`); 

--
-- Indexes for table `course_unit`
--
CREATE UNIQUE INDEX `course_unit_uniqueness` ON `course_unit`  (`course_unit_id`,`course_id`,`year`,`semester`); 
CREATE INDEX `course_unit_course_id` ON `course_unit` (`course_id`);

--
-- Indexes for table `faculty`
--
CREATE UNIQUE INDEX `faculty_acronym` ON `faculty`(`acronym`);

--
-- Indexes for table `schedule`
--
CREATE INDEX `schedule_course_unit_id` ON `schedule`(`course_unit_id`);
