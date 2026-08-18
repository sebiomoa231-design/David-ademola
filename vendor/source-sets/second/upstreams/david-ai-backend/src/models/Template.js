const mongoose = require('mongoose');

const templateSchema = new mongoose.Schema(
  {
    title: { type: String, required: true },
    category: { type: String, enum: ['video', 'motion-library', 'image'], required: true },
    thumbnailUrl: { type: String, required: true },
    // What applying "Try Now" actually does - a starter prompt/config
    // for the relevant tool.
    tool: { type: String, enum: ['image', 'video', 'artwork'], required: true },
    presetPrompt: { type: String, default: '' },
    presetOptions: { type: mongoose.Schema.Types.Mixed, default: {} }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Template', templateSchema);
