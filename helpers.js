// helpers.js — serialisers, token, order ID, WhatsApp
'use strict';
const jwt   = require('jsonwebtoken');
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

const JWT_SECRET  = process.env.JWT_SECRET  || 'nkyam_dev_secret_CHANGE_IN_PROD';
const JWT_EXPIRES = process.env.JWT_EXPIRES || '7d';
const GREEN_ID    = process.env.GREEN_API_ID    || '';
const GREEN_TOK   = process.env.GREEN_API_TOKEN || '';
const GREEN_URL   = `https://7107.api.greenapi.com/waInstance${GREEN_ID}/sendMessage/${GREEN_TOK}`;
const ADMIN_WA    = process.env.ADMIN_WHATSAPP  || '2347034547179@c.us';
const WA_ON       = process.env.WHATSAPP_ENABLED !== 'false' && !!GREEN_ID && !!GREEN_TOK;

function fmtUser(row) {
  return {
    userId: row.user_id, fullName: row.full_name, email: row.email,
    phone: row.phone || null, whatsappNumber: row.whatsapp_number || null,
    role: row.role, createdAt: row.created_at || null,
  };
}

function fmtOrder(row) {
  return {
    orderId: row.order_id, userId: row.user_id || null,
    customerName: row.customer_name, phone: row.phone,
    deliveryAddress: row.delivery_address, yamType: row.yam_type,
    pricePerTuber: Number(row.price_per_tuber),
    quantity: Number(row.quantity), totalPrice: Number(row.total_price),
    status: row.status, notes: row.notes || null,
    createdAt: row.created_at || null, updatedAt: row.updated_at || null,
  };
}

function genOrderId() { return uuidv4().replace(/-/g, '').slice(0, 8).toUpperCase(); }

function makeToken(userId, role) {
  return jwt.sign({ sub: userId, role }, JWT_SECRET, { expiresIn: JWT_EXPIRES });
}

function notifyWhatsApp(order) {
  if (!WA_ON) return;
  const msg = [
    `🍠 *NEW ORDER — NK's Yams*`, '',
    `Order ID : #${order.orderId}`,  `Customer : ${order.customerName}`,
    `Phone    : ${order.phone}`,     `Address  : ${order.deliveryAddress}`,
    `Yam      : ${order.yamType}`,   `Price/ea : ₦${Number(order.pricePerTuber).toLocaleString('en-NG')}`,
    `Qty      : ${order.quantity}`,  `Total    : ₦${Number(order.totalPrice).toLocaleString('en-NG')}`,
    `Time     : ${new Date().toLocaleString('en-NG')}`,
  ].join('\n');
  axios.post(GREEN_URL, { chatId: ADMIN_WA, message: msg }, { timeout: 10000 })
       .catch(e => console.warn('WhatsApp failed:', e.message));
}

module.exports = { fmtUser, fmtOrder, genOrderId, makeToken, notifyWhatsApp, JWT_SECRET };
