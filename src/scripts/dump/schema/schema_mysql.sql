-- Database: `tts` FOR POSTGRES
--

-- --------------------------------------------------------

--
-- Table structure for table `faculty`
--

CREATE TABLE faculty (
  acronym VARCHAR(10) PRIMARY KEY,
  name TEXT,
  last_updated TIMESTAMP NOT NULL
);

-- --------------------------------------------------------
--
-- Table structure for table `course`
--

CREATE TABLE course (
  id SERIAL PRIMARY KEY,
  faculty_id VARCHAR(10) NOT NULL,
  name VARCHAR(200) NOT NULL,
  acronym VARCHAR(10) NOT NULL,
  course_type VARCHAR(50) NOT NULL,
  year INT NOT NULL,
  url VARCHAR(2000) NOT NULL,
  plan_url VARCHAR(2000) NOT NULL,
  last_updated TIMESTAMP NOT NULL,
  FOREIGN KEY (faculty_id) REFERENCES faculty(acronym) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX course_faculty_id_idx ON course (faculty_id);

-- --------------------------------------------------------
--
-- Table structure for table `course_unit`
--

CREATE TABLE course_unit (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  acronym VARCHAR(16) NOT NULL,
  recent_occr INT NOT NULL,
  last_updated TIMESTAMP NOT NULL
);


-- --------------------------------------------------------
--
-- Table structure for table `course_metadata`
--
CREATE TABLE course_course_unit (
  course_id INT NOT NULL,
  course_unit_id INT NOT NULL,
  year SMALLINT NOT NULL,
  semester VARCHAR(10) NOT NULL,
  ects FLOAT(4) NOT NULL,
  PRIMARY KEY (course_id, course_unit_id, year, semester),
  FOREIGN KEY (course_unit_id) REFERENCES course_unit(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (course_id) REFERENCES course(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX course_course_unit_course_unit_id_idx ON course_course_unit (course_unit_id);
CREATE INDEX course_course_unit_course_id_idx ON course_course_unit (course_id);



CREATE TABLE professor (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL
);

-- --------------------------------------------------------

--
-- Table structure for table `course_unit_professor`
--

CREATE TABLE course_unit_professor (
  course_unit_id INT NOT NULL,
  professor_id INT NOT NULL,
  PRIMARY KEY (course_unit_id, professor_id),
  FOREIGN KEY (course_unit_id) REFERENCES course_unit(id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY (professor_id) REFERENCES professor(id) ON DELETE CASCADE ON UPDATE CASCADE
);


-- --------------------------------------------------------
------------------------------------------------
--
-- Table structure for table `info`
--

CREATE TABLE info (
  date TIMESTAMP PRIMARY KEY
);
