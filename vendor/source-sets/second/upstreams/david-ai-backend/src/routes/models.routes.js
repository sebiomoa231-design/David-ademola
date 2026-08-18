const express = require('express');
const { listModelsForTool } = require('../controllers/models.controller');

const router = express.Router();

router.get('/:tool', listModelsForTool);

module.exports = router;
