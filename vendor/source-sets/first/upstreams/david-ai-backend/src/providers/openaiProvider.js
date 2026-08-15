const native = require('./nativeProvider');

/**
 * Adapter for OpenAI's GPT Image 2.
 * INTEGRATION POINT: see the note in googleProvider.js - same pattern here.
 */
async function generate({ tool, modelId, prompt, options }) {
  if (!process.env.OPENAI_API_KEY) {
    return native.generate({ tool, modelId, prompt, options });
  }

  // TODO: replace with a real call, e.g. OpenAI's images API:
  // const res = await fetch('https://api.openai.com/v1/images/generations', {
  //   method: 'POST',
  //   headers: {
  //     Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
  //     'Content-Type': 'application/json'
  //   },
  //   body: JSON.stringify({ model: 'gpt-image-2', prompt, ...options })
  // });
  // const data = await res.json();
  // return { resultUrl: data.data[0].url, thumbnailUrl: data.data[0].url, isMock: false };

  throw Object.assign(
    new Error('OPENAI_API_KEY is set but the real OpenAI provider call is not implemented yet - see src/providers/openaiProvider.js'),
    { status: 501 }
  );
}

module.exports = { generate };
