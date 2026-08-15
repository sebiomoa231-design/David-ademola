const express = require('express');
const { requireAuth } = require('../middleware/auth');
const {
  createGeneration,
  listMyCreations,
  getCreation,
  likeCreation,
  setCreationVisibility
} = require('../controllers/generation.controller');

const router = express.Router();

// All generation endpoints require a logged-in user.
router.use(requireAuth);

router.post('/generate/:tool', createGeneration);
router.get('/creations', listMyCreations);
router.get('/creations/:id', getCreation);
router.post('/creations/:id/like', likeCreation);
router.patch('/creations/:id/visibility', setCreationVisibility);

module.exports = router;
