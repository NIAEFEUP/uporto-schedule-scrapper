const express = require('express');
const bodyParser = require('body-parser');

const models = require('./models');

const port = process.env.PORT || 8080;
const app = express();

const router = express.Router();

app.use(bodyParser.json());

router.get('/faculties', (req, res) => {
  models.faculty.findAll().then((faculties) => {
    res.send(faculties);
  });
});

app.use('/', router);
app.listen(port);