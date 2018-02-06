const express = require('express');
const bodyParser = require('body-parser');
const Sequelize = require('sequelize');
const cors = require('cors');

const models = require('./models');

const port = process.env.PORT || 8080;
const app = express();

const router = express.Router();

app.use(cors());
app.use(bodyParser.json());

/*
 * Get all courses
 */
router.get('/courses', (req, res) => {
  models.course.findAll().then((courses) => {
    res.send(courses);
  });
});

/*
 * Get all course units from a course taught on a given year and semester
 * Still need to implement the year in the database itself
 */
router.get('/courses/:courseId/:year/:semester/units', (req, res) => {
  models.courseUnit.findAll({
    where: {
      course_id: req.params.courseId,
      year: req.params.year,
      semester: req.params.semester
    }
  }).then((result) => {
    res.send(result);
  });
});

/*
 * Get all course units from a course
 */
router.get('/courses/:courseId/units', (req, res) => {
  models.courseUnit.findAll({
    where: {
      course_id: req.params.courseId
    }
  }).then((result) => {
    res.send(result);
  });
});

/*
 * Get all course units
 */
router.get('/course-units', (req, res) => {
  models.courseUnit.findAll().then((courseUnits) => {
    res.send(courseUnits);
  });
});

/*
 * Get all schedules from a course unit
 */
router.get('/course-units/:unitId/schedules', (req, res) => {
  models.schedule.findAll({
    where: {
      course_unit_id: req.params.unitId
    }
  }).then((result) => {
    res.send(result);
  });
});

/*
 * Get all faculties
 */
router.get('/faculties', (req, res) => {
  models.faculty.findAll().then((faculties) => {
    res.send(faculties);
  });
});

/*
 * Get a list of courses from a faculty
 */
router.get('/faculties/:facultyId/courses', (req, res) => {
  models.course.findAll({
    where: {
      faculty_id: req.params.facultyId
    }
  }).then((result) => {
    res.send(result);
  });
});

/*
 * Get all schedules
 */
router.get('/schedules', (req, res) => {
  models.schedule.findAll().then((schedules) => {
    res.send(schedules);
  });
});

/*
 * Get all schedules from a course
 * In a list divided by years
 */
router.get('/courses/:courseId/schedules', (req, res) => {
  models.courseUnit.findAll({
    include: [{
      model: models.schedule,
    }],
    where: {
      course_id: req.params.courseId,
    },
    order: [
      ['course_year', 'DESC']
    ]
  }).then((schedules) => {
    res.send(schedules)
  });
});

/*
 * Get all schedules all course units taught in the given year and semester
 * from a specific course in a list divided by years
 */
router.get('/courses/:courseId/:year/:semester/schedules', (req, res) => {
  models.courseUnit.findAll({
    include: [{
      model: models.schedule,
    }],
    where: {
      course_id: req.params.courseId,
      year: req.params.year,
      semester: req.params.semester
    },
    order: [
      ['course_year', 'DESC']
    ]
  }).then((schedules) => {
    res.send(schedules)
  });
});

app.use('/', router);
app.listen(port);