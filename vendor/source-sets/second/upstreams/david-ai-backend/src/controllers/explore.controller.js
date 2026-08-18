const asyncHandler = require('express-async-handler');
const Creation = require('../models/Creation');

/**
 * GET /api/explore?tab=popular|styles&tool=image&page=1&limit=30
 * Powers the Explore page's masonry grid and the "Popular"/"Styles" tabs,
 * and doubles as the feed for Home's "Get Inspired" section (just call
 * it with a smaller `limit`).
 */
const listExplore = asyncHandler(async (req, res) => {
  const { tab = 'popular', tool } = req.query;
  const page = Math.max(parseInt(req.query.page, 10) || 1, 1);
  const limit = Math.min(parseInt(req.query.limit, 10) || 30, 60);

  const filter = { isPublic: true, status: 'completed' };
  if (tool) filter.tool = tool;

  const sort = tab === 'styles' ? { createdAt: -1 } : { likeCount: -1, createdAt: -1 };

  const [items, total] = await Promise.all([
    Creation.find(filter)
      .sort(sort)
      .skip((page - 1) * limit)
      .limit(limit)
      .populate('user', 'name avatarColor'),
    Creation.countDocuments(filter)
  ]);

  res.json({ tab, items, page, limit, total, hasMore: page * limit < total });
});

module.exports = { listExplore };
