const asyncHandler = require('express-async-handler');
const Template = require('../models/Template');

/**
 * GET /api/templates?category=video|motion-library|image
 * Powers the Templates page's three tabs. Category is optional -
 * omit it to get everything (e.g. for an admin view).
 */
const listTemplates = asyncHandler(async (req, res) => {
  const { category } = req.query;
  const filter = {};
  if (category) filter.category = category;

  const templates = await Template.find(filter).sort({ createdAt: -1 });
  res.json({ templates });
});

module.exports = { listTemplates };
