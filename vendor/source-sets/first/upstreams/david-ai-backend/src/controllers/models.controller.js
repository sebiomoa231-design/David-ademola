const asyncHandler = require('express-async-handler');
const { getModelsForTool, TOOLS } = require('../config/modelsRegistry');

/**
 * GET /api/models/:tool
 * Powers the "Select Model" dropdown on Image/Video/etc. Returns the
 * exact list the frontend renders, in order, with the default flagged.
 */
const listModelsForTool = asyncHandler(async (req, res) => {
  const { tool } = req.params;
  const models = getModelsForTool(tool);
  if (!models) {
    return res.status(404).json({ error: `Unknown tool "${tool}". Valid tools: ${TOOLS.join(', ')}` });
  }
  res.json({ tool, models });
});

module.exports = { listModelsForTool };
