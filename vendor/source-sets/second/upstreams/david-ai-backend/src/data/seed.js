/**
 * Seeds a demo user, a handful of Templates (matching the Templates
 * page's Video / Motion Library / Image tabs), and a page of public
 * Creations so Explore and Home's "Get Inspired" aren't empty on
 * first run.
 *
 * Run with: npm run seed
 */
require('dotenv').config();
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const connectDB = require('../config/db');
const User = require('../models/User');
const Template = require('../models/Template');
const Creation = require('../models/Creation');

const TEMPLATES = [
  { title: 'Skyline Banner', category: 'image', tool: 'image', thumbnailUrl: 'https://placehold.co/600x800/111319/D6A15A?text=Skyline+Banner', presetPrompt: 'A person standing on a rooftop holding a blank banner, city skyline behind them, golden hour' },
  { title: 'Disco Ball Logo', category: 'image', tool: 'image', thumbnailUrl: 'https://placehold.co/600x800/111319/D6A15A?text=Disco+Ball+Logo', presetPrompt: 'A logo rendered as a reflective disco ball, studio lighting, colorful reflections' },
  { title: 'Family Toon', category: 'image', tool: 'artwork', thumbnailUrl: 'https://placehold.co/600x800/111319/D6A15A?text=Family+Toon', presetPrompt: 'Turn this family photo into a warm Pixar-style cartoon' },
  { title: 'Cinematic Walk', category: 'motion-library', tool: 'video', thumbnailUrl: 'https://placehold.co/600x800/111319/D6A15A?text=Cinematic+Walk', presetOptions: { motion: 'slow-dolly-forward' } },
  { title: 'Product Spin', category: 'motion-library', tool: 'video', thumbnailUrl: 'https://placehold.co/600x800/111319/D6A15A?text=Product+Spin', presetOptions: { motion: '360-turntable' } },
  { title: 'Wedding Portrait Reel', category: 'video', tool: 'video', thumbnailUrl: 'https://placehold.co/600x800/111319/D6A15A?text=Wedding+Reel', presetPrompt: 'Bride and groom portrait, soft cinematic motion, shallow depth of field' }
];

async function seed() {
  await connectDB();

  const email = 'demo@davidai.dev';
  let user = await User.findOne({ email });
  if (!user) {
    const passwordHash = await bcrypt.hash('demo-password', 10);
    user = await User.create({ name: 'Demo User', email, passwordHash });
    console.log('[seed] created demo user:', email, '(password: demo-password)');
  }

  await Template.deleteMany({});
  await Template.insertMany(TEMPLATES);
  console.log(`[seed] inserted ${TEMPLATES.length} templates`);

  await Creation.deleteMany({ user: user._id });
  const sampleCreations = Array.from({ length: 12 }).map((_, i) => ({
    user: user._id,
    tool: i % 2 === 0 ? 'image' : 'artwork',
    prompt: `Sample public creation #${i + 1}`,
    modelId: i % 2 === 0 ? 'nano-banana-pro' : 'davinci-ultra',
    provider: i % 2 === 0 ? 'google' : 'native',
    status: 'completed',
    resultUrl: `https://placehold.co/800x800/111319/D6A15A?text=Sample+${i + 1}`,
    thumbnailUrl: `https://placehold.co/400x400/111319/D6A15A?text=Sample+${i + 1}`,
    isMock: true,
    isPublic: true,
    likeCount: Math.floor(Math.random() * 500)
  }));
  await Creation.insertMany(sampleCreations);
  console.log(`[seed] inserted ${sampleCreations.length} sample public creations`);

  await mongoose.disconnect();
  console.log('[seed] done');
}

seed().catch((err) => {
  console.error('[seed] failed:', err);
  process.exit(1);
});
