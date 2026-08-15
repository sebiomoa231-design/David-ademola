const jwt = require('jsonwebtoken');

/**
 * Verifies the Bearer token on the Authorization header and attaches
 * { id, email } to req.user. Use on any route that requires a logged-in user.
 */
function requireAuth(req, res, next) {
  const header = req.headers.authorization || '';
  const token = header.startsWith('Bearer ') ? header.slice(7) : null;

  if (!token) {
    return res.status(401).json({ error: 'Missing or invalid Authorization header.' });
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.user = { id: payload.sub, email: payload.email };
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token.' });
  }
}

/**
 * Like requireAuth, but doesn't fail the request if there's no token -
 * it just leaves req.user undefined. Useful for routes like /explore
 * that behave slightly differently for logged-in users but don't require it.
 */
function attachUserIfPresent(req, res, next) {
  const header = req.headers.authorization || '';
  const token = header.startsWith('Bearer ') ? header.slice(7) : null;
  if (!token) return next();

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    req.user = { id: payload.sub, email: payload.email };
  } catch (err) {
    // ignore invalid token for optional auth
  }
  next();
}

module.exports = { requireAuth, attachUserIfPresent };
