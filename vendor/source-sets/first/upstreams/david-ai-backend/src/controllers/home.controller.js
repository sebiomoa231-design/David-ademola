const asyncHandler = require('express-async-handler');
const Creation = require('../models/Creation');
const Template = require('../models/Template');
const { MODELS } = require('../config/modelsRegistry');

/**
 * GET /api/home
 * One aggregated payload for the Home screen, so the frontend doesn't
 * have to make five separate requests on first load:
 *   - featured image/video models (for the two "Explore models" carousels)
 *   - a handful of featured templates (for "Explore Creative Templates")
 *   - a page of public creations (for "Get Inspired")
 */
const getHome = asyncHandler(async (req, res) => {
  const [featuredTemplates, getInspired] = await Promise.all([
    Template.find({}).sort({ createdAt: -1 }).limit(6),
    Creation.find({ isPublic: true, status: 'completed' })
      .sort({ createdAt: -1 })
      .limit(24)
      .populate('user', 'name avatarColor')
  ]);

  res.json({
    imageModels: MODELS.image,
    videoModels: MODELS.video,
    featuredTemplates,
    getInspired
  });
});

module.exports = { getHome };
