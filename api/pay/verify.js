// Verifies the Razorpay signature server-side, then asks Razorpay which
// product the order was for. Without both checks anyone could POST a fake
// success, or pay for the cheap product and claim the expensive one.
const crypto = require('crypto');

const KEY_ID = process.env.RAZORPAY_KEY_ID;
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

  const expected = crypto.createHmac('sha256', KEY_SECRET)
    .update(`${orderId}|${paymentId}`).digest('hex');
  const a = Buffer.from(expected);
  const c = Buffer.from(String(signature));
  if (a.length !== c.length || !crypto.timingSafeEqual(a, c)) {
    return res.status(400).json({ ok: false, error: 'signature mismatch' });
  }

  // Which product was actually paid for? Ask Razorpay, not the browser.
  let product = null;
  try {
    const auth = 'Basic ' + Buffer.from(`${KEY_ID}:${KEY_SECRET}`).toString('base64');
    const r = await fetch(`https://api.razorpay.com/v1/orders/${encodeURIComponent(orderId)}`,
      { headers: { Authorization: auth } });
    const order = await r.json();
    if (r.ok && order && order.notes) product = order.notes.product || null;
    if (r.ok && order && order.status === 'paid') { /* settled */ }
  } catch (err) {
    console.error('order lookup failed', err && err.message);
  }
  if (!product) return res.status(502).json({ ok: false, error: 'could not confirm product' });

  // Best-effort sale log; a storage hiccup must not block a paid download.
  if (KV_URL && KV_TOKEN) {
    try {
      await fetch(`${KV_URL}/incr/sales:${encodeURIComponent(product)}`,
        { headers: { Authorization: `Bearer ${KV_TOKEN}` } });
      await fetch(`${KV_URL}/set/sale:${encodeURIComponent(paymentId)}/${encodeURIComponent(product)}`,
        { headers: { Authorization: `Bearer ${KV_TOKEN}` } });
    } catch (err) {
      console.error('sale log failed', err && err.message);
    }
  }

  // A grant lets the browser fetch the answer key for a solved product later,
  // without us having to trust anything it says.
  const grant = crypto.createHmac('sha256', KEY_SECRET)
    .update(`${product}|${paymentId}`).digest('hex');

  return res.status(200).json({ ok: true, product: product, paymentId: paymentId, grant: grant });
};
