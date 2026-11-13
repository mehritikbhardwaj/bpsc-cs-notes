// Serves the answer keys to readers who bought the "solved" product.
// The answers never ship in the page, so a grant is required: an HMAC the
// verify step issues after Razorpay confirms a solved purchase.
const crypto = require('crypto');

const KEY_SECRET = process.env.RAZORPAY_KEY_SECRET;
const KV_URL = process.env.KV_REST_API_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN;

const SETS = { 'bpsc-pyq-solved': 'sol:bpsc', 'stet-pyq-solved': 'sol:stet' };

function sign(product, paymentId) {
  return crypto.createHmac('sha256', KEY_SECRET).update(`${product}|${paymentId}`).digest('hex');
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
  if (!KEY_SECRET || !KV_URL || !KV_TOKEN) return res.status(503).json({ error: 'not configured' });

  const b = req.body || {};
  const product = String(b.product || '');
  const paymentId = String(b.paymentId || '');
  const grant = String(b.grant || '');
  const key = SETS[product];
  if (!key || !paymentId || !grant) return res.status(400).json({ error: 'missing fields' });

  const expected = Buffer.from(sign(product, paymentId));
  const given = Buffer.from(grant);
  if (expected.length !== given.length || !crypto.timingSafeEqual(expected, given)) {
    return res.status(403).json({ error: 'invalid grant' });
  }

  try {
    const r = await fetch(`${KV_URL}/get/${key}`, { headers: { Authorization: `Bearer ${KV_TOKEN}` } });
    const d = await r.json();
    if (!r.ok || !d.result) return res.status(502).json({ error: 'answers unavailable' });
    return res.status(200).json({ answers: JSON.parse(d.result) });
  } catch (err) {
    console.error('solutions fetch failed', err && err.message);
    return res.status(502).json({ error: 'answers unavailable' });
  }
};
