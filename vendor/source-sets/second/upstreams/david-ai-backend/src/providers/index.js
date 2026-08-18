const google = require('./googleProvider');
const openai = require('./openaiProvider');
const bytedance = require('./bytedanceProvider');
const xai = require('./xaiProvider');
const native = require('./nativeProvider');

const ADAPTERS = { google, openai, bytedance, xai, native };

/**
 * Routes a generation request to the adapter named by `providerName`
 * (from the models registry entry). Falls back to the native/mock
 * adapter if the provider name is unrecognized, so a bad/typo'd
 * provider field never hard-crashes a generation request.
 */
async function generate(providerName, payload) {
  const adapter = ADAPTERS[providerName] || native;
  return adapter.generate(payload);
}

module.exports = { generate, ADAPTERS };
