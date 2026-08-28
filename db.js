// db.js — Neon PostgreSQL pool + schema init
'use strict';
const { Pool, types } = require('pg');

types.setTypeParser(1114, s => s);
types.setTypeParser(1184, s => s);
types.setTypeParser(1700, s => parseFloat(s));

let pool = null;
const DB_URL = (process.env.DATABASE_URL || '').trim();

if (DB_URL) {
  pool = new Pool({
    connectionString: DB_URL,
    ssl: { rejectUnauthorized: false },
    max: 10,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 6000,
  });
  pool.on('error', err => console.error('DB pool error:', err.message));
}

async function db(sql, params = []) {
  if (!pool) throw Object.assign(new Error('DATABASE_URL is not configured.'), { status: 503 });
  const client = await pool.connect();
  try { return await client.query(sql, params); }
  finally { client.release(); }
}

async function pingDB() {
  const r = await db('SELECT NOW() AS now');
  return r.rows[0].now;
}

async function initDB() {
  await db(`CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY, user_id VARCHAR(36) UNIQUE NOT NULL,
    full_name VARCHAR(120) NOT NULL, email VARCHAR(180) UNIQUE NOT NULL,
    phone VARCHAR(20), whatsapp_number VARCHAR(20),
    password_hash TEXT NOT NULL, role VARCHAR(20) NOT NULL DEFAULT 'customer',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ)`);

  await db(`ALTER TABLE users ADD COLUMN IF NOT EXISTS whatsapp_number VARCHAR(20)`);
  await db(`ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ`);

  await db(`CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY, order_id VARCHAR(8) UNIQUE NOT NULL,
    user_id VARCHAR(36) REFERENCES users(user_id) ON DELETE SET NULL,
    customer_name VARCHAR(120) NOT NULL, phone VARCHAR(20) NOT NULL,
    delivery_address TEXT NOT NULL, yam_type VARCHAR(50) NOT NULL,
    price_per_tuber INT NOT NULL, quantity INT NOT NULL,
    total_price INT NOT NULL, status VARCHAR(30) NOT NULL DEFAULT 'pending',
    notes TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), updated_at TIMESTAMPTZ)`);

  await db(`ALTER TABLE orders ADD COLUMN IF NOT EXISTS notes TEXT`);
  await db(`ALTER TABLE orders ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ`);
  await db(`CREATE INDEX IF NOT EXISTS idx_orders_user_id  ON orders(user_id)`);
  await db(`CREATE INDEX IF NOT EXISTS idx_orders_status   ON orders(status)`);
  await db(`CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id)`);
  await db(`CREATE INDEX IF NOT EXISTS idx_users_email     ON users(email)`);
  console.log('✅  Database schema ready.');
}

module.exports = { db, pingDB, initDB, pool: () => pool };
