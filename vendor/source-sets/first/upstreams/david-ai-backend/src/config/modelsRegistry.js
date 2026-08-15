/**
 * Single source of truth for every generation model David AI exposes,
 * grouped by tool. This powers the "Select Model" dropdown on each
 * tool page and is what src/providers/index.js uses to route a
 * generation request to the right adapter.
 *
 * To add a model: add an entry here, then make sure providers/<provider>.js
 * knows how to handle its id (or let it fall through to the native mock).
 */
const MODELS = {
  image: [
    { id: 'nano-banana-pro', name: 'Nano Banana Pro', provider: 'google', description: 'Photorealistic visuals ideal for ads and text', default: true },
    { id: 'nano-banana-2', name: 'Nano Banana 2', provider: 'google', description: 'State-of-the-art image generation with advanced editing and composition' },
    { id: 'nano-banana', name: 'Nano Banana', provider: 'google', description: 'Stunning photorealistic visuals for any idea' },
    { id: 'gpt-image-2', name: 'GPT Image 2', provider: 'openai', description: 'State-of-the-art image generation with unmatched realism, typography, and control' },
    { id: 'seedream-5', name: 'Seedream 5.0', provider: 'bytedance', description: 'Fast, lightweight generation with strong visual quality' },
    { id: 'seedream-4-5', name: 'Seedream 4.5', provider: 'bytedance', description: 'Enhanced aesthetics with improved visual fidelity' },
    { id: 'grok-pro', name: 'Grok Pro', provider: 'xai', description: 'xAI Grok high-quality image generation' },
    { id: 'davinci-ultra', name: 'DaVinci Ultra', provider: 'native', description: "DaVinci's legacy model, optimized for high quality results" }
  ],
  video: [
    { id: 'seedance-2', name: 'Seedance 2.0', provider: 'bytedance', description: 'Balanced motion quality, prompt adherence, and price performance', default: true },
    { id: 'kling-3', name: 'Kling 3.0', provider: 'bytedance', description: 'Strong motion quality and cinematic camera control' },
    { id: 'davinci-motion', name: 'DaVinci Motion', provider: 'native', description: "DaVinci's in-house fast model for quick video drafts" }
  ],
  artwork: [
    { id: 'davinci-ultra', name: 'DaVinci Ultra', provider: 'native', description: 'Style-preset artwork generation', default: true }
  ],
  music: [
    { id: 'davinci-music', name: 'DaVinci Music', provider: 'native', description: 'Mood- and theme-driven music generation', default: true }
  ],
  voice: [
    { id: 'davinci-voice', name: 'DaVinci Voice', provider: 'native', description: 'Text-to-speech and voiceover generation', default: true }
  ],
  enhancer: [
    { id: 'davinci-enhancer', name: 'DaVinci Enhancer', provider: 'native', description: 'Upscales images up to 22K resolution and adds new detail', default: true }
  ],
  editor: [
    { id: 'davinci-editor', name: 'DaVinci Editor', provider: 'native', description: 'General-purpose asset editing', default: true }
  ]
};

const TOOLS = Object.keys(MODELS);

function getModelsForTool(tool) {
  return MODELS[tool] || null;
}

function getModelById(tool, modelId) {
  const list = MODELS[tool];
  if (!list) return null;
  return list.find((m) => m.id === modelId) || null;
}

function getDefaultModel(tool) {
  const list = MODELS[tool];
  if (!list) return null;
  return list.find((m) => m.default) || list[0] || null;
}

module.exports = { MODELS, TOOLS, getModelsForTool, getModelById, getDefaultModel };
