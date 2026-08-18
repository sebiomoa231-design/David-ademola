const express = require('express');
const { listTemplates } = require('../controllers/templates.controller');

const router = express.Router();

router.get('/', listTemplates);

module.exports = router;
