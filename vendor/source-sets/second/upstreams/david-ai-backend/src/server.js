require('dotenv').config();
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');

const connectDB = require('./config/db');
const { notFound, errorHandler } = require('./middleware/errorHandler');

const authRoutes = require('./routes/auth.routes');
const modelsRoutes = require('./routes/models.routes');
const generationRoutes = require('./routes/generation.routes');
const exploreRoutes = require('./routes/explore.routes');
const templatesRoutes = require('./routes/templates.routes');
const homeRoutes = require('./routes/home.routes');

const app = express();

app.use(cors({ origin: process.env.CLIENT_ORIGIN || '*' }));
app.use(express.json({ limit: '10mb' }));
app.use(morgan('dev'));

app.get('/health', (req, res) => res.json({ ok: true, service: 'david-ai-creative-backend' }));

// Route map:
//   /api/auth/*        register, login, me
//   /api/models/:tool   the model list for a tool's "Select Model" dropdown
//   /api/home           aggregated Home-screen payload
//   /api/explore        Explore page feed + Home's "Get Inspired"
//   /api/templates      Templates page feed
//   /api/generate/:tool + /api/creations/*   generation jobs (image/video/artwork/music/voice/enhancer/editor)
app.use('/api/auth', authRoutes);
app.use('/api/models', modelsRoutes);
app.use('/api/home', homeRoutes);
app.use('/api/explore', exploreRoutes);
app.use('/api/templates', templatesRoutes);
app.use('/api', generationRoutes);

app.use(notFound);
app.use(errorHandler);

const PORT = process.env.PORT || 4000;

async function start() {
  await connectDB();
  app.listen(PORT, () => {
    console.log(`[server] David AI creative backend listening on port ${PORT}`);
  });
}

start();

module.exports = app;
