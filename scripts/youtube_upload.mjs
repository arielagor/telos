#!/usr/bin/env node
/**
 * Upload a video to YouTube (Unlisted) via the Data API v3 resumable upload.
 *
 * Reuses the existing Google OAuth client at ~/.gbrain/google-oauth.json (the same
 * desktop client the GBrain collectors use). Mints a SEPARATE token with the
 * youtube.upload scope at ~/.gbrain/youtube-tokens.json so it never clobbers the
 * gmail/calendar token. One browser consent click is needed the first time.
 *
 * Usage:
 *   node youtube_upload.mjs <video.mp4> <title> <description-file> [unlisted|private|public]
 *
 * Prints the watch URL on success.
 */
import { createServer } from 'http';
import { execFile } from 'child_process';

// Open a URL in the default browser without a shell (no command injection surface).
function openBrowser(url) {
  try {
    if (process.platform === 'win32') execFile('cmd', ['/c', 'start', '', url]);
    else if (process.platform === 'darwin') execFile('open', [url]);
    else execFile('xdg-open', [url]);
  } catch { /* user can open the printed URL manually */ }
}
import { readFileSync, writeFileSync, existsSync, statSync, openSync, readSync, closeSync } from 'fs';
import { join } from 'path';
import { URL } from 'url';

const HOME = process.env.HOME || process.env.USERPROFILE;
const GB = join(HOME, '.gbrain');
const OAUTH = JSON.parse(readFileSync(join(GB, 'google-oauth.json'), 'utf8'));
const TOKEN_FILE = join(GB, 'youtube-tokens.json');
const CLIENT_ID = OAUTH.client_id, CLIENT_SECRET = OAUTH.client_secret;
const SCOPE = 'https://www.googleapis.com/auth/youtube.upload';
const PORT = 8914, REDIRECT = `http://localhost:${PORT}`;

const [, , VIDEO, TITLE, DESC_FILE, VIS = 'unlisted'] = process.argv;
if (!VIDEO || !TITLE) { console.error('usage: youtube_upload.mjs <video> <title> <desc-file> [vis]'); process.exit(2); }
const DESCRIPTION = DESC_FILE && existsSync(DESC_FILE) ? readFileSync(DESC_FILE, 'utf8') : '';

async function exchange(body) {
  const r = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams(body),
  });
  return r.json();
}

async function consentFlow() {
  return new Promise((resolve, reject) => {
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${encodeURIComponent(CLIENT_ID)}&redirect_uri=${encodeURIComponent(REDIRECT)}` +
      `&response_type=code&scope=${encodeURIComponent(SCOPE)}&access_type=offline&prompt=consent`;
    const server = createServer(async (req, res) => {
      const u = new URL(req.url, REDIRECT);
      const code = u.searchParams.get('code'), err = u.searchParams.get('error');
      if (err) { res.end(`Auth failed: ${err}`); server.close(); return reject(new Error(err)); }
      if (!code) { res.end('waiting...'); return; }
      const tok = await exchange({ code, client_id: CLIENT_ID, client_secret: CLIENT_SECRET, redirect_uri: REDIRECT, grant_type: 'authorization_code' });
      if (tok.error) { res.end('token error'); server.close(); return reject(new Error(tok.error_description || tok.error)); }
      const data = { ...tok, expiry_date: Date.now() + tok.expires_in * 1000, obtained_at: new Date().toISOString() };
      writeFileSync(TOKEN_FILE, JSON.stringify(data, null, 2));
      res.end('<h2 style="color:green">YouTube upload authorized. You can close this tab.</h2>');
      server.close(); resolve(data);
    });
    server.listen(PORT, () => {
      console.log('\n>>> Open this URL and approve YouTube upload access (one time):\n' + authUrl + '\n');
      openBrowser(authUrl);
    });
    setTimeout(() => { server.close(); reject(new Error('consent timeout (5 min)')); }, 300000);
  });
}

async function getAccessToken() {
  if (existsSync(TOKEN_FILE)) {
    const t = JSON.parse(readFileSync(TOKEN_FILE, 'utf8'));
    if (t.refresh_token) {
      const r = await exchange({ client_id: CLIENT_ID, client_secret: CLIENT_SECRET, refresh_token: t.refresh_token, grant_type: 'refresh_token' });
      if (r.access_token) return r.access_token;
    }
  }
  const fresh = await consentFlow();
  return fresh.access_token;
}

async function upload(accessToken) {
  const size = statSync(VIDEO).size;
  const meta = { snippet: { title: TITLE, description: DESCRIPTION, categoryId: '28' }, status: { privacyStatus: VIS, selfDeclaredMadeForKids: false } };
  // 1) start resumable session
  const start = await fetch('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status', {
    method: 'POST',
    headers: { Authorization: `Bearer ${accessToken}`, 'Content-Type': 'application/json',
      'X-Upload-Content-Length': String(size), 'X-Upload-Content-Type': 'video/*' },
    body: JSON.stringify(meta),
  });
  if (!start.ok) { console.error('start failed', start.status, await start.text()); process.exit(1); }
  const location = start.headers.get('location');
  console.log('resumable session started; uploading', (size / 1048576).toFixed(1), 'MB...');
  // 2) PUT the bytes (single shot; 54MB is fine in one request)
  const buf = Buffer.alloc(size);
  const fd = openSync(VIDEO, 'r'); readSync(fd, buf, 0, size, 0); closeSync(fd);
  const put = await fetch(location, { method: 'PUT', headers: { 'Content-Length': String(size), 'Content-Type': 'video/*' }, body: buf });
  const out = await put.json();
  if (!put.ok || !out.id) { console.error('upload failed', put.status, JSON.stringify(out)); process.exit(1); }
  console.log('\nUPLOADED:', `https://youtu.be/${out.id}`);
  console.log('WATCH_URL=https://www.youtube.com/watch?v=' + out.id);
  console.log('STUDIO=https://studio.youtube.com/video/' + out.id + '/edit');
}

(async () => { const at = await getAccessToken(); await upload(at); })().catch(e => { console.error('ERROR:', e.message); process.exit(1); });
