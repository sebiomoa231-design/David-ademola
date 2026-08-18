const express = require('express');
const { listExplore } = require('../controllers/explore.controller');

const router = express.Router();

router.get('/', listExplore);

module.exports = router;
