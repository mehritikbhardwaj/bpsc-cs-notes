// Records what readers are looking for, so we can see demand. Best effort:
// the browser hands off to WhatsApp either way.
const KV_URL = process.env.KV_REST_API_URL;
const KV_TOKEN = process.env.KV_REST_API_TOKEN;

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, max-age=0');
  if (req.method !== 'POST') return res.status(405).json({ ok: false });

  const q = String((req.body && req.body.q) || '').slice(0, 300).trim();
  const page = String((req.body && req.body.page) || '').slice(0, 120);
  if (!q) return res.status(400).json({ ok: false });
  if (!KV_URL || !KV_TOKEN) return res.status(200).json({ ok: true });

  try {
    const entry = JSON.stringify({ q, page, at: new Date().toISOString() });
    await fetch(`${KV_URL}/lpush/asks/${encodeURIComponent(entry)}`,
      { headers: { Authorization: `Bearer ${KV_TOKEN}` } });
    await fetch(`${KV_URL}/ltrim/asks/0/499`,
      { headers: { Authorization: `Bearer ${KV_TOKEN}` } });
  } catch (err) {
    console.error('ask log failed', err && err.message);
  }
  return res.status(200).json({ ok: true });
};
