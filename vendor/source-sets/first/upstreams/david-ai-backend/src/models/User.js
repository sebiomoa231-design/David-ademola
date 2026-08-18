const mongoose = require('mongoose');

const userSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true },
    email: { type: String, required: true, unique: true, lowercase: true, trim: true },
    passwordHash: { type: String, required: true },
    plan: { type: String, enum: ['free', 'pro'], default: 'free' },
    avatarColor: { type: String, default: '#D6A15A' }
  },
  { timestamps: true }
);

module.exports = mongoose.model('User', userSchema);
