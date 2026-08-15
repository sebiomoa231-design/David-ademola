const native = require('./nativeProvider');

/**
 * Adapter for ByteDance's models (Seedream for image, Seedance for video).
 * INTEGRATION POINT: see the note in googleProvider.js - same pattern here.
 */
async function generate({ tool, modelId, prompt, options }) {
  if (!process.env.BYTEDANCE_API_KEY) {
    return native.generate({ tool, modelId, prompt, options });
  }

  // TODO: replace with a real call to ByteDance/Doubao's API once you
  // have credentials and their current endpoint + request shape.

  throw Object.assign(
    new Error('BYTEDANCE_API_KEY is set but the real ByteDance provider call is not implemented yet - see src/providers/bytedanceProvider.js'),
    { status: 501 }
  );
}

module.exports = { generate };
