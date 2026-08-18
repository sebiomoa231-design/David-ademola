const native = require('./nativeProvider');

/**
 * Adapter for xAI's Grok Pro image model.
 * INTEGRATION POINT: see the note in googleProvider.js - same pattern here.
 */
async function generate({ tool, modelId, prompt, options }) {
  if (!process.env.XAI_API_KEY) {
    return native.generate({ tool, modelId, prompt, options });
  }

  // TODO: replace with a real call to xAI's API once you have
  // credentials and their current endpoint + request shape.

  throw Object.assign(
    new Error('XAI_API_KEY is set but the real xAI provider call is not implemented yet - see src/providers/xaiProvider.js'),
    { status: 501 }
  );
}

module.exports = { generate };
