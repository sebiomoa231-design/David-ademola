const { v4: uuidv4 } = require('uuid');

/**
 * The "native" provider is DaVinci's own in-house model, AND it doubles
 * as the mock/fallback generator every other provider uses when its real
 * API key isn't configured yet (see providers/index.js). That means the
 * whole app is runnable and demoable the moment you `npm install`, before
 * you've wired up a single real API key.
 *
 * Swap the body of `generate()` for a real in-house model call when ready,
 * or leave it as the permanent fallback - it's a legitimate design choice
 * to always have a working default.
 */
async function generate({ tool, modelId, prompt, options = {} }) {
  // Simulate generation latency so the frontend's pending/processing
  // states have something real to show.
  await new Promise((resolve) => setTimeout(resolve, 1200));

  const id = uuidv4();
  const placeholders = {
    image: `https://placehold.co/1024x1024/111319/D6A15A?text=${encodeURIComponent('Image ' + id.slice(0, 8))}`,
    video: `https://placehold.co/1024x576/111319/D6A15A?text=${encodeURIComponent('Video ' + id.slice(0, 8))}`,
    artwork: `https://placehold.co/1024x1024/111319/D6A15A?text=${encodeURIComponent('Artwork ' + id.slice(0, 8))}`,
    music: `https://placehold.co/512x512/111319/D6A15A?text=${encodeURIComponent('Track ' + id.slice(0, 8))}`,
    voice: `https://placehold.co/512x512/111319/D6A15A?text=${encodeURIComponent('Voice ' + id.slice(0, 8))}`,
    enhancer: `https://placehold.co/1024x1024/111319/D6A15A?text=${encodeURIComponent('Enhanced ' + id.slice(0, 8))}`,
    editor: `https://placehold.co/1024x1024/111319/D6A15A?text=${encodeURIComponent('Edited ' + id.slice(0, 8))}`
  };

  return {
    resultUrl: placeholders[tool] || placeholders.image,
    thumbnailUrl: placeholders[tool] || placeholders.image,
    isMock: true,
    providerRef: id
  };
}

module.exports = { generate };
