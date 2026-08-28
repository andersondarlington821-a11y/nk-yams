// ============================================================
//  NK's Yams — Node.js/Express API Server v3
//  Complete production-ready backend with Neon PostgreSQL
// ============================================================
'use strict';

require('dotenv').config();

const express = require('express');
const cors = require('cors');
const path = require('path');
const bcrypt = require('bcryptjs');

const { db, pingDB, initDB, pool } = require('./db');
const { fmtUser, fmtOrder, genOrderId, makeToken, notifyWhatsApp } = require('./helpers');
const { requireJWT, requireAdmin } = require('./middleware');

// ── CONFIG ───────────────────────────────────────────────────
const PORT = parseInt(process.env.PORT || '5000', 10);
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || '7Xk9mP2nQ8rS5tU3vW7yZ4bC6dF8gH1jL9';
const YAM_TYPES = ['Water Yam', 'Yellow Yam', 'White Yam'];
const STATUSES = ['pending', 'confirmed', 'dispatched', 'delivered', 'cancelled'];
const MIN_P = 1000, MAX_P = 3000;

// ── EXPRESS APP ──────────────────────────────────────────────
const app = express();

app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Admin-Token'],
}));
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));

// ── ROUTES ───────────────────────────────────────────────────

// Health check
app.get('/health', async (_req, res) => {
  let dbTime = null;
  const hasPool = !!pool();
  if (hasPool) { try { dbTime = await pingDB(); } catch { /* ok */ } }
  res.json({ status: 'OK', timestamp: new Date().toISOString(), db: hasPool, dbTime });
});

// AUTH: Register
app.post('/api/auth/register', async (req, res) => {
  try {
    const { fullName = '', email = '', phone = '', whatsappNumber = '', password = '' } = req.body || {};

    const name = fullName.trim();
    const mail = email.trim().toLowerCase();
    const tel = phone.trim().replace(/\D/g, '').slice(0, 11);
    const wa = (whatsappNumber.trim() || tel).replace(/\D/g, '').slice(0, 11);

    if (name.length < 2)
      return res.status(400).json({ success: false, message: 'Full name must be at least 2 characters.' });
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(mail))
      return res.status(400).json({ success: false, message: 'A valid email address is required.' });
    if (!password || password.length < 6)
      return res.status(400).json({ success: false, message: 'Password must be at least 6 characters.' });
    if (tel && (tel.length < 10 || tel.length > 11))
      return res.status(400).json({ success: false, message: 'Phone number must be 10 or 11 digits.' });

    const { v4: uuidv4 } = require('uuid');
    const uid = uuidv4();
    const hash = await bcrypt.hash(password, 12);

    const r = await db(
      `INSERT INTO users (user_id,full_name,email,phone,whatsapp_number,password_hash,role)
       VALUES ($1,$2,$3,$4,$5,$6,'customer') RETURNING *`,
      [uid, name, mail, tel || null, wa || null, hash]
    );

    const token = makeToken(uid, 'customer');
    return res.status(201).json({ success: true, message: 'Account created!', token, user: fmtUser(r.rows[0]) });

  } catch (err) {
    if (err.code === '23505')
      return res.status(409).json({ success: false, message: 'An account with that email already exists.' });
    console.error('[register]', err.message);
    return res.status(500).json({ success: false, message: 'Server error. Please try again.' });
  }
});

// AUTH: Login
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email = '', password = '' } = req.body || {};
    const mail = email.trim().toLowerCase();
    if (!mail || !password)
      return res.status(400).json({ success: false, message: 'Email and password are required.' });

    const r = await db('SELECT * FROM users WHERE email=$1', [mail]);
    const row = r.rows[0];
    if (!row || !(await bcrypt.compare(password, row.password_hash)))
      return res.status(401).json({ success: false, message: 'Invalid email or password.' });

    const token = makeToken(row.user_id, row.role);
    return res.json({ success: true, message: 'Logged in!', token, user: fmtUser(row) });

  } catch (err) {
    console.error('[login]', err.message);
    return res.status(500).json({ success: false, message: 'Server error. Please try again.' });
  }
});

// AUTH: Get current user
app.get('/api/auth/me', requireJWT, async (req, res) => {
  try {
    const r = await db('SELECT * FROM users WHERE user_id=$1', [req.userId]);
    if (!r.rows[0]) return res.status(404).json({ success: false, message: 'User not found.' });
    return res.json({ success: true, user: fmtUser(r.rows[0]) });
  } catch (err) {
    console.error('[me]', err.message);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// ORDERS: My orders (MUST be before /:orderId route)
app.get('/api/orders/mine', requireJWT, async (req, res) => {
  try {
    const r = await db('SELECT * FROM orders WHERE user_id=$1 ORDER BY created_at DESC', [req.userId]);
    return res.json({ success: true, orders: r.rows.map(fmtOrder) });
  } catch (err) {
    console.error('[orders/mine]', err.message);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// ORDERS: Track by ID (public)
app.get('/api/orders/:orderId', async (req, res) => {
  try {
    const r = await db('SELECT * FROM orders WHERE order_id=$1', [req.params.orderId.toUpperCase()]);
    if (!r.rows[0]) return res.status(404).json({ success: false, message: 'Order not found.' });
    return res.json({ success: true, order: fmtOrder(r.rows[0]) });
  } catch (err) {
    console.error('[track]', err.message);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// ORDERS: Create order (JWT required)
app.post('/api/orders', requireJWT, async (req, res) => {
  try {
    const { customerName = '', phone = '', deliveryAddress = '', yamType, pricePerTuber, quantity } = req.body || {};
    const name = customerName.trim();
    const tel = phone.trim();
    const addr = deliveryAddress.trim();
    const price = Number(pricePerTuber);
    const qty = Math.round(Number(quantity));

    if (name.length < 2)
      return res.status(400).json({ success: false, message: 'Full name required.' });
    if (!tel || tel.replace(/\D/g, '').length < 7)
      return res.status(400).json({ success: false, message: 'Valid phone number required.' });
    if (addr.length < 5)
      return res.status(400).json({ success: false, message: 'Delivery address required.' });
    if (!YAM_TYPES.includes(yamType))
      return res.status(400).json({ success: false, message: `Yam type must be one of: ${YAM_TYPES.join(', ')}.` });
    if (isNaN(price) || price < MIN_P || price > MAX_P)
      return res.status(400).json({ success: false, message: `Price per tuber must be ₦${MIN_P.toLocaleString('en-NG')}–₦${MAX_P.toLocaleString('en-NG')}.` });
    if (!Number.isInteger(qty) || qty < 1)
      return res.status(400).json({ success: false, message: 'Quantity must be at least 1.' });

    const orderId = genOrderId();
    const totalPrice = price * qty;

    const r = await db(
      `INSERT INTO orders (order_id,user_id,customer_name,phone,delivery_address,yam_type,price_per_tuber,quantity,total_price,status)
       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,'pending') RETURNING *`,
      [orderId, req.userId, name, tel, addr, yamType, price, qty, totalPrice]
    );

    const order = fmtOrder(r.rows[0]);
    setImmediate(() => notifyWhatsApp(order));

    return res.status(201).json({ success: true, message: 'Order placed!', orderId, order });

  } catch (err) {
    console.error('[create order]', err.message);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// ADMIN: Get all orders (with filter + search)
app.get('/api/admin/orders', requireAdmin, async (req, res) => {
  try {
    const { status, search } = req.query;
    const clauses = ['1=1'];
    const params = [];

    if (status && status !== 'all') {
      params.push(status);
      clauses.push(`status=$${params.length}`);
    }
    if (search && search.trim()) {
      const s = `%${search.trim()}%`;
      params.push(s, s, s);
      const n = params.length;
      clauses.push(`(customer_name ILIKE $${n - 2} OR phone ILIKE $${n - 1} OR order_id ILIKE $${n})`);
    }

    const r = await db(`SELECT * FROM orders WHERE ${clauses.join(' AND ')} ORDER BY created_at DESC`, params);
    return res.json({ success: true, count: r.rows.length, orders: r.rows.map(fmtOrder) });

  } catch (err) {
    console.error('[admin/orders]', err.message);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// ADMIN: Update order status
app.post('/api/admin/orders/:orderId/status', requireAdmin, async (req, res) => {
  try {
    const { status, notes } = req.body || {};
    if (!STATUSES.includes(status))
      return res.status(400).json({ success: false, message: `Status must be one of: ${STATUSES.join(', ')}.` });

    const r = await db(
      `UPDATE orders SET status=$1,notes=$2,updated_at=NOW() WHERE order_id=$3 RETURNING *`,
      [status, notes || null, req.params.orderId.toUpperCase()]
    );
    if (!r.rows[0]) return res.status(404).json({ success: false, message: 'Order not found.' });
    return res.json({ success: true, order: fmtOrder(r.rows[0]) });

  } catch (err) {
    console.error('[admin/status]', err.message);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// ADMIN: Delete order
app.delete('/api/admin/orders/:orderId', requireAdmin, async (req, res) => {
  try {
    const r = await db('DELETE FROM orders WHERE order_id=$1 RETURNING order_id', [req.params.orderId.toUpperCase()]);
    if (!r.rows[0]) return res.status(404).json({ success: false, message: 'Order not found.' });
    return res.json({ success: true, message: 'Order deleted.' });
  } catch (err) {
    console.error('[admin/del-order]', err.message);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// ADMIN: Get all users (with search)
app.get('/api/admin/users', requireAdmin, async (req, res) => {
  try {
    const { search } = req.query;
    const clauses = ['1=1'];
    const params = [];

    if (search && search.trim()) {
      const s = `%${search.trim()}%`;
      params.push(s, s, s);
      const n = params.length;
      clauses.push(`(full_name ILIKE $${n - 2} OR email ILIKE $${n - 1} OR phone ILIKE $${n})`);
    }

    const r = await db(`SELECT * FROM users WHERE ${clauses.join(' AND ')} ORDER BY created_at DESC`, params);
    return res.json({ success: true, count: r.rows.length, users: r.rows.map(fmtUser) });

  } catch (err) {
    console.error('[admin/users]', err.message);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// ADMIN: Delete user
app.delete('/api/admin/users/:userId', requireAdmin, async (req, res) => {
  try {
    const r = await db('DELETE FROM users WHERE user_id=$1 RETURNING user_id', [req.params.userId]);
    if (!r.rows[0]) return res.status(404).json({ success: false, message: 'User not found.' });
    return res.json({ success: true, message: 'User deleted.' });
  } catch (err) {
    console.error('[admin/del-user]', err.message);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// ADMIN: Dashboard stats
app.get('/api/admin/stats', requireAdmin, async (req, res) => {
  try {
    const [total, revenue, pending, confirmed, dispatched, delivered, cancelled, users, week] = await Promise.all([
      db('SELECT COUNT(*) AS c FROM orders'),
      db(`SELECT COALESCE(SUM(total_price),0) AS c FROM orders WHERE status!='cancelled'`),
      db(`SELECT COUNT(*) AS c FROM orders WHERE status='pending'`),
      db(`SELECT COUNT(*) AS c FROM orders WHERE status='confirmed'`),
      db(`SELECT COUNT(*) AS c FROM orders WHERE status='dispatched'`),
      db(`SELECT COUNT(*) AS c FROM orders WHERE status='delivered'`),
      db(`SELECT COUNT(*) AS c FROM orders WHERE status='cancelled'`),
      db('SELECT COUNT(*) AS c FROM users'),
      db(`SELECT COUNT(*) AS c FROM orders WHERE created_at >= NOW()-INTERVAL '7 days'`),
    ]);

    return res.json({
      success: true,
      totalOrders: parseInt(total.rows[0].c, 10),
      revenue: parseInt(revenue.rows[0].c, 10),
      pending: parseInt(pending.rows[0].c, 10),
      confirmed: parseInt(confirmed.rows[0].c, 10),
      dispatched: parseInt(dispatched.rows[0].c, 10),
      delivered: parseInt(delivered.rows[0].c, 10),
      cancelled: parseInt(cancelled.rows[0].c, 10),
      totalUsers: parseInt(users.rows[0].c, 10),
      weekOrders: parseInt(week.rows[0].c, 10),
    });

  } catch (err) {
    console.error('[admin/stats]', err.message);
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// Catch-all: serve index.html for non-API routes
app.get('*', (_req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Global error handler
app.use((err, _req, res, _next) => {
  const status = err.status || 500;
  console.error(`[unhandled ${status}]`, err.message);
  res.status(status).json({ success: false, message: err.message || 'Internal server error.' });
});

// ── STARTUP ──────────────────────────────────────────────────
async function start() {
  const bar = '='.repeat(56);
  console.log(`\n${bar}\n   NK's YAMS — Node.js API Server v3\n${bar}`);

  const hasPool = !!pool();
  if (!hasPool) {
    console.warn('\n  ⚠️  DATABASE_URL not set in .env');
    console.warn('  All /api/* endpoints will return 503.');
    console.warn('  Get your connection string from https://console.neon.tech\n');
  } else {
    try {
      console.log('\n  Connecting to Neon PostgreSQL...');
      const t = await pingDB();
      console.log(`  ✅  Connected — DB time: ${t}`);
      await initDB();
    } catch (err) {
      console.error('\n  ❌  DB connection FAILED:', err.message);
      console.error('  Check DATABASE_URL in .env\n');
    }
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n  ✅  Server running at http://localhost:${PORT}`);
    console.log(`  🌐  Frontend: /public`);
    console.log(`  🔑  Admin token: ${ADMIN_TOKEN.slice(0, 10)}...`);
    console.log(`\n${bar}\n`);
  });
}

start();
