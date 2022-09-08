BEGIN TRANSACTION;
CREATE TABLE `course` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `course_id` int(11) NOT NULL,
  `faculty_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `acronym` varchar(10) NOT NULL,
  `course_type` varchar(2) NOT NULL,
  `year` int(11) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `plan_url` varchar(2000) NOT NULL,
  `last_updated` datetime NOT NULL,
  FOREIGN KEY (`faculty_id`) REFERENCES `faculty`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE `course_unit` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `course_unit_id` int(11) NOT NULL,
  `course_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `acronym` varchar(16) NOT NULL,
  `url` varchar(2000) NOT NULL,
  `course_year` tinyint(4) NOT NULL,
  `semester` tinyint(4) NOT NULL,
  `year` smallint(6) NOT NULL,
  `schedule_url` varchar(2000) DEFAULT NULL,
  `last_updated` datetime NOT NULL,
  FOREIGN KEY (`course_id`) REFERENCES `course`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE `faculty` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `acronym` varchar(10) DEFAULT NULL,
  `name` text,
  `last_updated` datetime NOT NULL
);
INSERT INTO "faculty" VALUES(1,'faup','Faculdade de Arquitetura
','2022-09-08 12:37:08.291317');
INSERT INTO "faculty" VALUES(2,'fbaup','Faculdade de Belas Artes
','2022-09-08 12:37:08.350607');
INSERT INTO "faculty" VALUES(3,'fcup','Faculdade de Ciências
','2022-09-08 12:37:08.368156');
INSERT INTO "faculty" VALUES(4,'fcnaup','Faculdade de Ciências da Nutrição e da Alimentação
','2022-09-08 12:37:08.386430');
INSERT INTO "faculty" VALUES(5,'fadeup','Faculdade de Desporto
','2022-09-08 12:37:08.404982');
INSERT INTO "faculty" VALUES(6,'fdup','Faculdade de Direito
','2022-09-08 12:37:08.422693');
INSERT INTO "faculty" VALUES(7,'fep','Faculdade de Economia
','2022-09-08 12:37:08.441127');
INSERT INTO "faculty" VALUES(8,'feup','Faculdade de Engenharia
','2022-09-08 12:37:08.463977');
INSERT INTO "faculty" VALUES(9,'ffup','Faculdade de Farmácia
','2022-09-08 12:37:08.481789');
INSERT INTO "faculty" VALUES(10,'flup','Faculdade de Letras
','2022-09-08 12:37:08.499567');
INSERT INTO "faculty" VALUES(11,'fmup','Faculdade de Medicina
','2022-09-08 12:37:08.516262');
INSERT INTO "faculty" VALUES(12,'fmdup','Faculdade de Medicina Dentária
','2022-09-08 12:37:08.532877');
INSERT INTO "faculty" VALUES(13,'fpceup','Faculdade de Psicologia e de Ciências da Educação
','2022-09-08 12:37:08.551512');
INSERT INTO "faculty" VALUES(14,'icbas','Instituto de Ciências Biomédicas Abel Salazar (ICBAS)
','2022-09-08 12:37:08.569125');
CREATE TABLE `schedule` (
  `id` INTEGER PRIMARY KEY AUTOINCREMENT,
  `day` tinyint(3) NOT NULL,
  `duration` decimal(3,1) NOT NULL,
  `start_time` decimal(3,1) NOT NULL,
  `location` varchar(16) NOT NULL,
  `lesson_type` varchar(3) NOT NULL,
  `teacher_acronym` varchar(16) NOT NULL,
  `course_unit_id` int(11) NOT NULL,
  `last_updated` datetime NOT NULL,
  `class_name` varchar(16) NOT NULL,
  `composed_class_name` varchar(16) DEFAULT NULL,
  FOREIGN KEY (`course_unit_id`) REFERENCES `course_unit` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('faculty',14);
CREATE UNIQUE INDEX `course_course_id` ON `course` (`course_id`,`faculty_id`,`year`);
CREATE INDEX `course_faculty_id` ON `course` (`faculty_id`);
CREATE UNIQUE INDEX `course_unit_uniqueness` ON `course_unit`  (`course_unit_id`,`course_id`,`year`,`semester`);
CREATE INDEX `course_unit_course_id` ON `course_unit` (`course_id`);
CREATE UNIQUE INDEX `faculty_acronym` ON `faculty`(`acronym`);
CREATE INDEX `schedule_course_unit_id` ON `schedule`(`course_unit_id`);
COMMIT;
