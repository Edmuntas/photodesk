const express = require('express');
const multer  = require('multer');
const path    = require('path');
const cors    = require('cors');
const fs      = require('fs');
require('dotenv').config();

const app  = express();
const PORT = process.env.PORT || 3001;

// ── Storage ───────────────────────────────────────────────────────────────────
const UPLOADS_DIR = process.env.UPLOADS_DIR
  ? path.resolve(process.env.UPLOADS_DIR)
  : path.join(__dirname, '..', '..', 'data', 'uploads');
const RESULTS_DIR = process.env.RESULTS_DIR
  ? path.resolve(process.env.RESULTS_DIR)
  : path.join(__dirname, '..', '..', 'data', 'results');
if (!fs.existsSync(UPLOADS_DIR)) fs.mkdirSync(UPLOADS_DIR, { recursive: true });
if (!fs.existsSync(RESULTS_DIR)) fs.mkdirSync(RESULTS_DIR, { recursive: true });

const upload = multer({
  dest: UPLOADS_DIR,
  limits: { fileSize: 30 * 1024 * 1024 },
});

// ── Middleware ────────────────────────────────────────────────────────────────
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static(path.join(__dirname, 'public')));
app.use('/uploads', express.static(UPLOADS_DIR));
app.use('/results', express.static(RESULTS_DIR));

// Suppress favicon 404 in browser console
app.get('/favicon.ico', (_req, res) => res.status(204).end());

// Serve declutter.html from apps/frontend/
app.get('/declutter', (_req, res) => {
  const p = path.join(__dirname, '..', 'frontend', 'declutter.html');
  if (fs.existsSync(p)) return res.sendFile(p);
  res.status(404).send('declutter.html not found at ' + p);
});

// ── Helpers ───────────────────────────────────────────────────────────────────
async function xaiPost(url, apiKey, body) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const text = await resp.text();
  let json;
  try { json = JSON.parse(text); } catch { json = { raw: text }; }
  if (!resp.ok) throw Object.assign(new Error(`HTTP ${resp.status}`), { status: resp.status, detail: json });
  return json;
}

function toDataURI(filePath, mime = 'image/jpeg') {
  const buf = fs.readFileSync(filePath);
  return `data:${mime};base64,${buf.toString('base64')}`;
}

function fileMime(originalname) {
  const ext = (originalname || '').split('.').pop().toLowerCase();
  return ext === 'png' ? 'image/png' : 'image/jpeg';
}

// ── Prompts (loaded from prompts.json, editable at runtime) ──────────────────
const PROMPTS_FILE = path.join(__dirname, '..', '..', 'core', 'ai', 'prompts.json');
let customPrompts = JSON.parse(fs.readFileSync(PROMPTS_FILE, 'utf8'));

function buildPrompt(roomType, mode) {
  const map       = mode === 'empty' ? customPrompts.empty : customPrompts.declutter;
  const base      = map[roomType] || map['по умолчанию'];
  const noDefects = roomType === 'дрон';
  const defect    = noDefects ? '' : '\n\n' + customPrompts.defectRule;
  return base + defect + '\n\n' + customPrompts.qualityFooter;
}

app.get('/api/prompts', (_req, res) => res.json(customPrompts));

app.put('/api/prompts', (req, res) => {
  try {
    customPrompts = req.body;
    fs.writeFileSync(PROMPTS_FILE, JSON.stringify(customPrompts, null, 2), 'utf8');
    res.json({ ok: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── Room Detection ─────────────────────────────────────────────────────────────
app.post('/api/detect-room', upload.single('image'), async (req, res) => {
  const apiKey = ((req.body || {}).apiKey || '').trim();
  if (!apiKey)   return res.status(401).json({ error: 'API key required' });
  if (!req.file) return res.status(400).json({ error: 'Image required' });

  try {
    const dataURI = toDataURI(req.file.path, fileMime(req.file.originalname));
    const result  = await xaiPost('https://api.x.ai/v1/chat/completions', apiKey, {
      model: 'grok-2-vision-1212',
      messages: [{
        role: 'user',
        content: [
          { type: 'image_url', image_url: { url: dataURI } },
          { type: 'text', text:
            'This is a real estate photo. Identify the room type.\n' +
            'Reply with EXACTLY ONE Russian word — no other text:\n' +
            'кухня / спальня / гостиная / ванная / коридор / балкон / двор / дрон / по умолчанию\n\n' +
            'кухня=kitchen, спальня=bedroom with bed, гостиная=living/dining room, ' +
            'ванная=bathroom/toilet/shower, коридор=hallway/entryway, ' +
            'балкон=balcony/terrace, двор=exterior/yard/facade/parking, ' +
            'дрон=aerial drone shot from above, по умолчанию=other/unclear.\n' +
            'Reply with ONLY the single Russian word.'
          }
        ]
      }],
      temperature: 0,
      max_tokens: 15,
    });

    const raw   = (result.choices?.[0]?.message?.content || '').trim().toLowerCase();
    const ROOMS = ['кухня','спальня','гостиная','ванная','коридор','балкон','двор','дрон'];
    const found = ROOMS.find(r => raw.includes(r)) || 'по умолчанию';
    res.json({ room_type: found });
  } catch (err) {
    console.error('[detect-room]', err.detail || err.message);
    res.json({ room_type: 'по умолчанию', error: String(err.message) });
  } finally {
    if (req.file) fs.unlink(req.file.path, () => {});
  }
});

// ── Session folder helpers ────────────────────────────────────────────────────
function sanitizeFolder(name) {
  // Remove path traversal and shell-special chars, collapse spaces/dashes
  return (name || '')
    .replace(/[\/\\\.]{2,}/g, '')
    .replace(/[<>:"|?*\x00-\x1f]/g, '')
    .replace(/\s+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 80) || 'Session_' + Date.now();
}

// ── Image Processing ──────────────────────────────────────────────────────────
app.post('/api/process-image', upload.single('image'), async (req, res) => {
  const body         = req.body || {};
  const apiKey       = (body.apiKey        || '').trim();
  const mode         = (body.mode          || 'empty').trim();
  const roomType     = (body.roomType      || 'по умолчанию').trim();
  const sessionSlug  = sanitizeFolder(body.sessionFolder);

  if (!apiKey)   return res.status(401).json({ error: 'API key required' });
  if (!req.file) return res.status(400).json({ error: 'Image required' });

  // Create session subfolder
  const sessionDir = path.join(RESULTS_DIR, sessionSlug);
  fs.mkdirSync(sessionDir, { recursive: true });

  const stem = path.basename(req.file.originalname, path.extname(req.file.originalname));

  // Save original alongside result for gallery before/after
  const origName = `${stem}_original.jpg`;
  const origPath = path.join(sessionDir, origName);
  if (!fs.existsSync(origPath)) {
    fs.copyFileSync(req.file.path, origPath);
  }

  const prompt  = buildPrompt(roomType, mode);
  const dataURI = toDataURI(req.file.path, fileMime(req.file.originalname));
  const rawB64  = dataURI.split(',')[1];
  const model   = body.model || 'aurora';

  // image field expects an object — try every known object schema
  // NOTE: aurora does not support a "size" parameter — omit it entirely
  const attempts = [
    { label: 'obj-url',      payload: { model, prompt, image: { url: dataURI } } },
    { label: 'obj-b64',      payload: { model, prompt, image: { b64_json: rawB64 } } },
    { label: 'obj-type-url', payload: { model, prompt, image: { type: 'base64', url: dataURI } } },
    { label: 'obj-type-b64', payload: { model, prompt, image: { type: 'base64', data: rawB64 } } },
    { label: 'arr-url',      payload: { model, prompt, image: [{ url: dataURI }] } },
    { label: 'arr-b64',      payload: { model, prompt, image: [{ b64_json: rawB64 }] } },
    { label: 'images-arr',   payload: { model, prompt, images: [dataURI] } },
  ];

  let lastErr = null;
  for (const { label, payload } of attempts) {
    try {
      console.log(`[process-image] trying format: ${label}`);
      const result = await xaiPost('https://api.x.ai/v1/images/edits', apiKey, payload);
      const item   = result?.data?.[0];
      if (!item) throw new Error('No data[0] in response: ' + JSON.stringify(result).slice(0, 300));

      let imgBuf;
      if (item.b64_json) {
        imgBuf = Buffer.from(item.b64_json, 'base64');
      } else if (item.url) {
        const imgResp = await fetch(item.url);
        imgBuf = Buffer.from(await imgResp.arrayBuffer());
      } else {
        throw new Error('No b64_json or url in response item: ' + JSON.stringify(item).slice(0, 200));
      }

      const suffix  = mode === 'empty' ? '_empty' : '_clean';
      const outName = `${stem}${suffix}_${Date.now()}.jpg`;
      const outPath = path.join(sessionDir, outName);
      fs.writeFileSync(outPath, imgBuf);

      console.log(`[process-image] success: ${sessionSlug}/${outName}`);
      if (req.file) fs.unlink(req.file.path, () => {});
      return res.json({
        success: true,
        resultUrl:   `/results/${sessionSlug}/${outName}`,
        originalUrl: `/results/${sessionSlug}/${origName}`,
        sessionFolder: sessionSlug,
      });

    } catch (err) {
      lastErr = err;
      const detail = JSON.stringify(err.detail || err.message).slice(0, 200);
      console.warn(`[process-image] ${label} failed (${err.status || '?'}): ${detail}`);
      if (err.status !== 422) break;
    }
  }

  if (req.file) fs.unlink(req.file.path, () => {});
  const detail = lastErr?.detail || lastErr?.message || String(lastErr);
  console.error('[process-image] all attempts failed:', JSON.stringify(detail).slice(0, 500));
  res.status(500).json({ error: String(lastErr?.message), detail });
});

// ── Sessions API ──────────────────────────────────────────────────────────────
app.get('/api/sessions', (_req, res) => {
  try {
    const entries = fs.readdirSync(RESULTS_DIR, { withFileTypes: true })
      .filter(e => e.isDirectory())
      .map(e => {
        const dir   = path.join(RESULTS_DIR, e.name);
        const files = fs.readdirSync(dir).filter(f => f.endsWith('.jpg') && !f.endsWith('_original.jpg'));
        const stat  = fs.statSync(dir);
        return { slug: e.name, name: e.name.replace(/_/g, ' '), count: files.length, created: stat.mtimeMs };
      })
      .filter(s => s.count > 0)
      .sort((a, b) => b.created - a.created);
    res.json(entries);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/sessions/:slug', (req, res) => {
  const slug    = sanitizeFolder(req.params.slug);
  const dir     = path.join(RESULTS_DIR, slug);
  if (!fs.existsSync(dir)) return res.status(404).json({ error: 'Session not found' });

  try {
    const all      = fs.readdirSync(dir).filter(f => f.endsWith('.jpg'));
    const originals = new Set(all.filter(f => f.endsWith('_original.jpg')));
    const results   = all.filter(f => !f.endsWith('_original.jpg'));

    const items = results.map(fname => {
      // stem of result: e.g. "IMG_0751_empty_1234" → base stem "IMG_0751"
      const baseStem = fname.replace(/_(empty|clean)_\d+\.jpg$/, '');
      const origFile = `${baseStem}_original.jpg`;
      return {
        name:        baseStem,
        resultUrl:   `/results/${slug}/${fname}`,
        originalUrl: originals.has(origFile) ? `/results/${slug}/${origFile}` : null,
      };
    });

    res.json({ slug, name: slug.replace(/_/g, ' '), items });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── Global error handler (catches multer errors, etc.) ────────────────────────
// eslint-disable-next-line no-unused-vars
app.use((err, _req, res, _next) => {
  const status = err.status || err.statusCode || 500;
  const message = err.code === 'LIMIT_FILE_SIZE'
    ? 'File too large (max 30MB)'
    : err.message || 'Internal server error';
  res.status(status).json({ error: message });
});

// ── Start ─────────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`\nPhotoDesk AI server running at http://localhost:${PORT}`);
  console.log(`Declutter UI: http://localhost:${PORT}/declutter\n`);
});
