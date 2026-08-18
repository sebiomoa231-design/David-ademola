const native = require('./nativeProvider');

/**
 * Adapter for Google's models (Nano Banana Pro / 2 / base, and Veo for
 * video should you add it to the registry).
 *
 * INTEGRATION POINT: once GOOGLE_API_KEY is set in .env, replace the
 * body below with a real fetch() to Google's API. Request/response
 * shapes vary by product and change over time, so rather than guess at
 * a contract that might be wrong, this stays a clearly-marked stub
 * until you drop in the real call - that's safer than shipping a fake
 * integration that looks real but silently fails.
 */
async function generate({ tool, modelId, prompt, options }) {
  if (!process.env.GOOGLE_API_KEY) {
    return native.generate({ tool, modelId, prompt, options });
  }

  // TODO: replace with a real call, e.g.:
  // const res = await fetch('https://<google-api-endpoint>', {
  //   method: 'POST',
  //   headers: { Authorization: `Bearer ${process.env.GOOGLE_API_KEY}` },
  //   body: JSON.stringify({ model: modelId, prompt, ...options })
  // });
  // const data = await res.json();
  // return { resultUrl: data.url, thumbnailUrl: data.thumbnailUrl, isMock: false };

  throw Object.assign(
    new Error('GOOGLE_API_KEY is set but the real Google provider call is not implemented yet - see src/providers/googleProvider.js'),
    { status: 501 }
  );
}

module.exports = { generate };
