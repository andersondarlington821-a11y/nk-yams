// middleware.js — JWT + Admin auth
'use strict';
const jwt = require('jsonwebtoken');
const { JWT_SECRET } = require('./helpers');
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || '7Xk9mP2nQ8rS5tU3vW7yZ4bC6dF8gH1jL9';

function requireJWT(req, res, next) {
  const auth = (req.headers.authorization || '').trim();
  if (!auth.startsWith('Bearer '))
    return res.status(401).json({ success: false, message: 'Missing or invalid token.' });
  try {
    const p = jwt.verify(auth.slice(7), JWT_SECRET);
    req.userId   = p.sub;
    req.userRole = p.role;
    next();
  } catch (err) {
    const msg = err.name === 'TokenExpiredError'
      ? 'Session expired. Please log in again.'
      : 'Invalid token. Please log in again.';
    return res.status(401).json({ success: false, message: msg });
  }
}

function requireAdmin(req, res, next) {
  const tok = (req.headers['x-admin-token'] || '').trim();
  if (!tok || tok !== ADMIN_TOKEN)
    return res.status(401).json({ success: false, message: 'Admin access required.' });
  next();
}

module.exports = { requireJWT, requireAdmin };
