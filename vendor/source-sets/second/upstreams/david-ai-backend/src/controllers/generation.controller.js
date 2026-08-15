const asyncHandler = require('express-async-handler');
const Creation = require('../models/Creation');
const providers = require('../providers');
const { getModelById, getDefaultModel, TOOLS } = require('../config/modelsRegistry');

/**
 * POST /api/generate/:tool
 * Body: { prompt, modelId?, options?, isPublic? }
 *
 * This is the single entry point every tool page (Image, Video, Artwork,
 * Music, Voice, Enhancer, Editor) posts to. It:
 *   1. validates the tool + model,
 *   2. creates a Creation record with status "processing",
 *   3. calls the right provider adapter,
 *   4. updates the record to "completed" or "failed",
 *   5. returns the finished Creation.
 *
 * It's written synchronous-await for simplicity (the mock provider
 * resolves in ~1.2s). For real, slower provider calls in production,
 * swap step 3-4 for a background job/queue and let the frontend poll
 * GET /api/creations/:id - the schema (status/resultUrl) already
 * supports that without any changes.
 */
const createGeneration = asyncHandler(async (req, res) => {
  const { tool } = req.params;
  if (!TOOLS.includes(tool)) {
    return res.status(404).json({ error: `Unknown tool "${tool}". Valid tools: ${TOOLS.join(', ')}` });
  }

  const { prompt = '', modelId, options = {}, isPublic = false } = req.body;

  const model = modelId ? getModelById(tool, modelId) : getDefaultModel(tool);
  if (!model) {
    return res.status(400).json({ error: `No valid model found for tool "${tool}" (modelId: ${modelId || 'not provided'}).` });
  }

  // Tool-specific minimal validation
  if ((tool === 'image' || tool === 'video' || tool === 'artwork') && !prompt && !options.sourceAssetUrl) {
    return res.status(400).json({ error: 'A prompt or a sourceAssetUrl is required for this tool.' });
  }
  if ((tool === 'enhancer' || tool === 'editor') && !options.sourceAssetUrl) {
    return res.status(400).json({ error: 'options.sourceAssetUrl (the uploaded asset) is required for this tool.' });
  }

  const creation = await Creation.create({
    user: req.user.id,
    tool,
    prompt,
    modelId: model.id,
    provider: model.provider,
    options,
    status: 'processing',
    isPublic
  });

  try {
    const result = await providers.generate(model.provider, { tool, modelId: model.id, prompt, options });

    creation.status = 'completed';
    creation.resultUrl = result.resultUrl;
    creation.thumbnailUrl = result.thumbnailUrl || result.resultUrl;
    creation.isMock = Boolean(result.isMock);
    await creation.save();
  } catch (err) {
    creation.status = 'failed';
    creation.errorMessage = err.message;
    await creation.save();
  }

  const status = creation.status === 'failed' ? 502 : 201;
  res.status(status).json({ creation });
});

/**
 * GET /api/creations?tool=image&status=completed&page=1&limit=20
 * The current user's own creations, newest first. Powers each tool's
 * "Creations" tab.
 */
const listMyCreations = asyncHandler(async (req, res) => {
  const { tool, status } = req.query;
  const page = Math.max(parseInt(req.query.page, 10) || 1, 1);
  const limit = Math.min(parseInt(req.query.limit, 10) || 20, 50);

  const filter = { user: req.user.id };
  if (tool) filter.tool = tool;
  if (status) filter.status = status;

  const [items, total] = await Promise.all([
    Creation.find(filter)
      .sort({ createdAt: -1 })
      .skip((page - 1) * limit)
      .limit(limit),
    Creation.countDocuments(filter)
  ]);

  res.json({ items, page, limit, total, hasMore: page * limit < total });
});

/**
 * GET /api/creations/:id
 * Fetch a single creation - also what the frontend would poll if you
 * move generation to a background queue later.
 */
const getCreation = asyncHandler(async (req, res) => {
  const creation = await Creation.findById(req.params.id);
  if (!creation) return res.status(404).json({ error: 'Creation not found.' });

  const isOwner = creation.user.toString() === req.user.id;
  if (!creation.isPublic && !isOwner) {
    return res.status(403).json({ error: 'This creation is private.' });
  }

  res.json({ creation });
});

/**
 * POST /api/creations/:id/like
 * Used from the Explore detail panel's heart/like count.
 */
const likeCreation = asyncHandler(async (req, res) => {
  const creation = await Creation.findByIdAndUpdate(
    req.params.id,
    { $inc: { likeCount: 1 } },
    { new: true }
  );
  if (!creation) return res.status(404).json({ error: 'Creation not found.' });
  res.json({ creation });
});

/**
 * PATCH /api/creations/:id/visibility
 * Body: { isPublic: boolean }
 * Lets a user publish/unpublish one of their own creations to Explore.
 */
const setCreationVisibility = asyncHandler(async (req, res) => {
  const creation = await Creation.findById(req.params.id);
  if (!creation) return res.status(404).json({ error: 'Creation not found.' });
  if (creation.user.toString() !== req.user.id) {
    return res.status(403).json({ error: 'You can only change visibility on your own creations.' });
  }
  creation.isPublic = Boolean(req.body.isPublic);
  await creation.save();
  res.json({ creation });
});

module.exports = {
  createGeneration,
  listMyCreations,
  getCreation,
  likeCreation,
  setCreationVisibility
};
