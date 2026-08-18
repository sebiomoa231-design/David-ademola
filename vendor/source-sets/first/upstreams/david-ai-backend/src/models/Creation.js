const mongoose = require('mongoose');

/**
 * A single generation job/result. Every tool (image, video, artwork,
 * music, voice, enhancer, editor) writes to this same collection so the
 * "Creations" tab, the Explore feed, and job-status polling can all
 * share one query surface instead of one table per tool.
 */
const creationSchema = new mongoose.Schema(
  {
    user: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    tool: {
      type: String,
      enum: ['image', 'video', 'artwork', 'music', 'voice', 'enhancer', 'editor'],
      required: true
    },
    prompt: { type: String, default: '' },
    modelId: { type: String, required: true },
    provider: { type: String, required: true },

    // Free-form per-tool options: aspectRatio, quality, duration, moodboardId,
    // styleId, mood, theme, voiceId, sourceAssetUrl, etc.
    options: { type: mongoose.Schema.Types.Mixed, default: {} },

    status: {
      type: String,
      enum: ['pending', 'processing', 'completed', 'failed'],
      default: 'pending'
    },
    resultUrl: { type: String, default: null },
    thumbnailUrl: { type: String, default: null },
    isMock: { type: Boolean, default: false }, // true when a provider API key isn't configured yet
    errorMessage: { type: String, default: null },

    isPublic: { type: Boolean, default: false }, // surfaced in /explore and Home's "Get Inspired"
    likeCount: { type: Number, default: 0 }
  },
  { timestamps: true }
);

creationSchema.index({ tool: 1, isPublic: 1, createdAt: -1 });
creationSchema.index({ user: 1, tool: 1, createdAt: -1 });

module.exports = mongoose.model('Creation', creationSchema);
