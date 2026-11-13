// Visible view counter. Storage: Upstash Redis (connect it in Vercel → Storage).
// Until it is connected this returns 503 and the badge simply stays hidden.
const BASE = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL;
const TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN;
const KEY = 'site:views';

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store, max-age=0');

  if (!BASE || !TOKEN) {
    return res.status(503).json({ error: 'counter not configured' });
  }

  // ?hit=1 counts this visit; anything else just reads the total.
  const cmd = req.query && req.query.hit === '1' ? 'incr' : 'get';

  try {
    const r = await fetch(`${BASE}/${cmd}/${KEY}`, {
      headers: { Authorization: `Bearer ${TOKEN}` },
    });
    if (!r.ok) throw new Error(`upstream ${r.status}`);
    const data = await r.json();
    return res.status(200).json({ views: Number(data.result) || 0 });
  } catch (err) {
    return res.status(502).json({ error: 'counter unavailable' });
  }
}
