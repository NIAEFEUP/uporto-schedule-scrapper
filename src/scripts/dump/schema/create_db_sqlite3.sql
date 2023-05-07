
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
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `faculty_id` varchar(10) NOT NULL,
  `sigarra_id` int(11) NOT NULL,
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
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `sigarra_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `acronym` varchar(16) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `semester` tinyint(4) NOT NULL,
  `year` smallint(6) NOT NULL,
  `schedule_url` varchar(2000) DEFAULT NULL,
  `last_updated` datetime NOT NULL,
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
-- Table structure for table `schedule`
--

CREATE TABLE `schedule` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `day` tinyint(3) NOT NULL,
  `duration` decimal(3,1) NOT NULL,
  `start_time` decimal(3,1) NOT NULL,
  `location` varchar(31) NOT NULL,
  `lesson_type` varchar(3) NOT NULL,
  `is_composed` boolean NOT NULL,
  `sigarra_id` int (11),
  `course_unit_id` int(11) NOT NULL,
  `last_updated` datetime NOT NULL,
  `class_name` varchar(31) NOT NULL,
  `composed_class_name` varchar(16) DEFAULT NULL,
  FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);

-- -------------------------------------------------------- 

--
-- Table structure for table `schedule_professor`
--

CREATE TABLE `schedule_professor` (
  `schedule_id` INTEGER NOT NULL,
  `professor_id` INTEGER NOT NULL,
  FOREIGN KEY (`schedule_id`) REFERENCES `schedule` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (`professor_id`) REFERENCES `professor` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY (`schedule_id`, `professor_id`)
);

-- -------------------------------------------------------- 

--
-- Table structure for table `professor`
--

CREATE TABLE `professor` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `professor_acronym` varchar(16),
  `professor_name` varchar(50)
);

-- -------------------------------------------------------- 

--
-- Indexes for dumped tables
--

--
-- Indexes for table `course`
--
CREATE UNIQUE INDEX `course_course_id` ON `course` (`sigarra_id`,`faculty_id`,`year`);
CREATE INDEX `course_faculty_id` ON `course` (`faculty_id`); 

--
-- Indexes for table `course_unit`
--
CREATE UNIQUE INDEX `course_unit_uniqueness` ON `course_unit`  (`sigarra_id`,`course_id`,`year`,`semester`); 
CREATE INDEX `course_unit_course_id` ON `course_unit` (`course_id`);

--
-- Indexes for table `faculty`
--
CREATE UNIQUE INDEX `faculty_acronym` ON `faculty`(`acronym`);

--
-- Indexes for table `schedule`
--
CREATE INDEX `schedule_course_unit_id` ON `schedule`(`course_unit_id`);

--
-- Indexes for table `schedule_professors`
-- 
CREATE INDEX `schedule_professor_schedule_id` ON `schedule_professor`(`schedule_id`);

--
-- Indexes for table `course_metadata`
-- 
CREATE INDEX `course_metadata_index` ON `course_metadata`(`course_id`, `course_unit_id`, `course_unit_year`);