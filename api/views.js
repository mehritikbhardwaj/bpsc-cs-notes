// Visible view counter. Storage: Upstash Redis.
// NOTE: credentials are hardcoded below at the owner's request. This repo is
// public, so treat this token as compromised and rotate it in the Upstash
// dashboard if the counter is ever tampered with. Vercel also injects the same
// values as env vars, which take priority over these fallbacks.
const FALLBACK_URL = 'https://oriented-narwhal-73778.upstash.io';
const FALLBACK_TOKEN = 'gQAAAAAAASAyAAIgcDEzYmRkOWZjNzdiYzU0ZTUzYTkzMzcxN2ZkYzkwZWNjOQ';

const BASE = process.env.KV_REST_API_URL || process.env.UPSTASH_REDIS_REST_URL || FALLBACK_URL;
const TOKEN = process.env.KV_REST_API_TOKEN || process.env.UPSTASH_REDIS_REST_TOKEN || FALLBACK_TOKEN;
const KEY = 'site:views';

module.exports = async function handler(req, res) {
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
};
