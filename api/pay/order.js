// Creates a Razorpay order. Price lives here, never in the browser, so the
// amount cannot be tampered with from the client.
const KEY_ID = process.env.RAZORPAY_KEY_ID;
const KEY_SECRET = process.env.RAZORPAY_KEY_SECRET;
const PRICE_PAISE = 13900; // ₹139

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  if (req.method !== 'POST') return res.status(405).json({ error: 'method not allowed' });
  if (!KEY_ID || !KEY_SECRET) return res.status(503).json({ error: 'payments not configured' });

  const auth = 'Basic ' + Buffer.from(`${KEY_ID}:${KEY_SECRET}`).toString('base64');
  try {
    const r = await fetch('https://api.razorpay.com/v1/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: auth },
      body: JSON.stringify({
        amount: PRICE_PAISE,
        currency: 'INR',
        receipt: 'csnotes_' + Date.now(),
        notes: { product: 'CS Notes complete PDF' },
      }),
    });
    const data = await r.json();
    if (!r.ok || !data.id) {
      console.error('razorpay order failed', r.status, data && data.error);
      return res.status(502).json({ error: 'could not start payment' });
    }
    return res.status(200).json({
      orderId: data.id,
      amount: data.amount,
      currency: data.currency,
      keyId: KEY_ID, // key_id is public by design; the secret never leaves the server
    });
  } catch (err) {
    console.error('razorpay order error', err && err.message);
    return res.status(502).json({ error: 'could not start payment' });
  }
};
