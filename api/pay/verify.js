// Verifies the Razorpay signature server-side. Without this check anyone could
// POST a fake success and unlock the download.
const crypto = require('crypto');

const KEY_SECRET = process.env.RAZORPAY_KEY_SECRET;
const KV_URL = process.env.KV_REST_API_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN;

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method not allowed' });
  if (!KEY_SECRET) return res.status(503).json({ ok: false, error: 'payments not configured' });

  const b = req.body || {};
  const orderId = b.razorpay_order_id;
  const paymentId = b.razorpay_payment_id;
  const signature = b.razorpay_signature;
  if (!orderId || !paymentId || !signature) {
    return res.status(400).json({ ok: false, error: 'missing fields' });
  }

  const expected = crypto
    .createHmac('sha256', KEY_SECRET)
    .update(`${orderId}|${paymentId}`)
    .digest('hex');

  const a = Buffer.from(expected);
  const c = Buffer.from(String(signature));
  const ok = a.length === c.length && crypto.timingSafeEqual(a, c);
  if (!ok) return res.status(400).json({ ok: false, error: 'signature mismatch' });

  // Best-effort sale log; a storage hiccup must not block a paid download.
  if (KV_URL && KV_TOKEN) {
    try {
      await fetch(`${KV_URL}/incr/sales:count`, { headers: { Authorization: `Bearer ${KV_TOKEN}` } });
      await fetch(`${KV_URL}/set/sale:${encodeURIComponent(paymentId)}/${encodeURIComponent(orderId)}`, {
        headers: { Authorization: `Bearer ${KV_TOKEN}` },
      });
    } catch (err) {
      console.error('sale log failed', err && err.message);
    }
  }

  return res.status(200).json({ ok: true });
};
