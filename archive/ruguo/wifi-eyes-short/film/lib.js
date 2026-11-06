// ------------------------------------------------------------------ core
// Every frame is a pure function of time. Seeded noise only (mulberry32).
const W = 1080, H = 1920, FPS = 30;
const PAPER = '#EFE8DA', PAPER2 = '#F6F1E6', INK = '#1B1916', FIG = '#6B6358';
const DARK = '#0E0D0C', DLINE = '#5A5248', DTEXT = '#ECE4D6';
const ACC = '#FF6A1A', HOT = '#FFD9B8';
const ACC_RGB = [255, 106, 26], HOT_RGB = [255, 222, 196], DARK_RGB = [14, 13, 12];
const DISPLAY = '"Noto Serif CJK SC"', UI = '"Noto Sans Mono CJK SC"';

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function hash(...k) {
  let h = 2166136261;
  for (const v of k) { h ^= (v * 2654435761) | 0; h = Math.imul(h, 16777619); }
  return mulberry32(h)();
}
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const ev = (t, t0, d) => clamp((t - t0) / d);
const smooth = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const ease = x => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const expoOut = x => { x = clamp(x); return x === 1 ? 1 : 1 - Math.pow(2, -10 * x); };
const expoIn = x => { x = clamp(x); return x === 0 ? 0 : Math.pow(2, 10 * x - 10); };
const expoInOut = x => { x = clamp(x); return x === 0 ? 0 : x === 1 ? 1 : x < 0.5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2; };
const backOut = x => { x = clamp(x); const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
// closed-form spring: 0 -> 1 with a small overshoot, settles in ~d seconds
const spring = (t, t0, d = 0.5) => { const x = Math.max(0, (t - t0) / d); return t < t0 ? 0 : 1 - Math.exp(-5.5 * x) * Math.cos(7.5 * x); };
const boil = t => Math.floor(t * FPS / 2);      // ink boils on 2s

// ------------------------------------------------------------------ canvas
const cv = document.getElementById('c');
let ctx = cv.getContext('2d');
cv.width = W; cv.height = H;
let Z = 1;           // current camera zoom (for constant screen-px line widths)
let CAM = { x: 0, y: 0, z: 1 };
let BT = 0;          // current boil index
const INKW = 1.35;   // global ink weight

function setCam(x, y, z) {
  CAM = { x, y, z }; Z = z;
  ctx.setTransform(z, 0, 0, z, W / 2 - x * z, H / 2 - y * z);
}
function screenCam() { CAM = { x: W / 2, y: H / 2, z: 1 }; Z = 1; ctx.setTransform(1, 0, 0, 1, 0, 0); }
const toScreen = (x, y) => [W / 2 + (x - CAM.x) * CAM.z, H / 2 + (y - CAM.y) * CAM.z];
const toWorld = (sx, sy) => [CAM.x + (sx - W / 2) / CAM.z, CAM.y + (sy - H / 2) / CAM.z];

// ------------------------------------------------------------------ ink
function jit(key, i, amt) { return (hash(key, i, BT) - 0.5) * 2 * amt; }
function subdiv(pts, step) {
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const [x0, y0] = pts[i], [x1, y1] = pts[i + 1];
    const n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / step));
    for (let k = 0; k < n; k++) out.push([lerp(x0, x1, k / n), lerp(y0, y1, k / n)]);
  }
  out.push(pts[pts.length - 1]);
  return out;
}
// a hand-inked polyline: wobbles on 2s, slight second pass
function ink(pts, px = 3, col = INK, o = {}) {
  const wob = (o.wob ?? 1.2) / Z, key = o.key ?? 7;
  const P = o.raw ? pts : subdiv(pts, (o.step ?? 60) / Z);
  ctx.strokeStyle = col; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.globalAlpha = o.alpha ?? 1;
  px *= INKW;
  ctx.lineWidth = px / Z;
  ctx.beginPath();
  P.forEach(([x, y], i) => {
    const X = x + jit(key, i * 2, wob), Y = y + jit(key, i * 2 + 1, wob);
    i ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y);
  });
  if (o.closed) ctx.closePath();
  ctx.stroke();
  if (!o.single && px >= 2.5) {   // a dry second pass reads as pen pressure
    ctx.globalAlpha = (o.alpha ?? 1) * 0.28;
    ctx.lineWidth = px * 0.55 / Z;
    ctx.beginPath();
    P.forEach(([x, y], i) => {
      const X = x + jit(key + 91, i * 2, wob * 1.6), Y = y + jit(key + 91, i * 2 + 1, wob * 1.6);
      i ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y);
    });
    if (o.closed) ctx.closePath();
    ctx.stroke();
  }
  ctx.globalAlpha = 1;
}
const rectPts = (x, y, w, h) => [[x, y], [x + w, y], [x + w, y + h], [x, y + h], [x, y]];
function inkRect(x, y, w, h, px, col, o = {}) { ink(rectPts(x, y, w, h), px, col, { ...o, closed: true }); }
function circlePts(cx, cy, r, n = 48, a0 = 0, a1 = Math.PI * 2) {
  const p = [];
  for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; p.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); }
  return p;
}
function inkCircle(cx, cy, r, px, col, o = {}) { ink(circlePts(cx, cy, r, o.n ?? 48), px, col, { ...o, raw: true }); }
function ellPts(cx, cy, rx, ry, n = 64, a0 = 0, a1 = Math.PI * 2) {
  const p = [];
  for (let i = 0; i <= n; i++) { const a = a0 + (a1 - a0) * i / n; p.push([cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]); }
  return p;
}
// parallel hatching inside the current path region (call after building a clip)
function hatch(x, y, w, h, ang, gap, px, col, alpha = 1, key = 3) {
  ctx.save();
  ctx.strokeStyle = col; ctx.lineWidth = px / Z; ctx.globalAlpha = alpha; ctx.lineCap = 'round';
  const c = Math.cos(ang), s = Math.sin(ang), R = Math.hypot(w, h);
  const cx = x + w / 2, cy = y + h / 2;
  ctx.beginPath();
  for (let d = -R / 2, i = 0; d <= R / 2; d += gap / Z, i++) {
    const j = jit(key, i, 0.8 / Z);
    ctx.moveTo(cx + c * -R / 2 - s * (d + j), cy + s * -R / 2 + c * (d + j));
    ctx.lineTo(cx + c * R / 2 - s * (d + j), cy + s * R / 2 + c * (d + j));
  }
  ctx.stroke();
  ctx.restore();
}
function hatchRect(x, y, w, h, ang, gap, px, col, alpha = 1, key = 3) {
  ctx.save(); ctx.beginPath(); ctx.rect(x, y, w, h); ctx.clip();
  hatch(x, y, w, h, ang, gap, px, col, alpha, key); ctx.restore();
}

// ------------------------------------------------------------------ type
function font(face, px, weight = 700) { ctx.font = `${weight} ${px}px ${face}`; }
function text(str, x, y, o = {}) {
  font(o.face ?? UI, o.size ?? 40, o.weight ?? 700);
  ctx.textAlign = o.align ?? 'left'; ctx.textBaseline = o.base ?? 'alphabetic';
  ctx.globalAlpha = o.alpha ?? 1;
  if (o.stroke) { ctx.lineJoin = 'round'; ctx.lineWidth = o.stroke; ctx.strokeStyle = o.strokeCol ?? DARK; ctx.strokeText(str, x, y); }
  ctx.fillStyle = o.color ?? INK; ctx.fillText(str, x, y);
  ctx.globalAlpha = 1;
}
// characters land one by one at given times; each lands with a short drop + overshoot (not a fade)
function writeOn(chars, x, y, times, t, o = {}) {
  font(o.face ?? DISPLAY, o.size ?? 120, o.weight ?? 700);
  ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
  const widths = chars.map(c => ctx.measureText(c.ch ?? c).width + (o.track ?? 0));
  const total = widths.reduce((a, b) => a + b, 0);
  let cx = o.align === 'center' ? x - total / 2 : o.align === 'right' ? x - total : x;
  chars.forEach((c, i) => {
    const ch = c.ch ?? c, col = c.col ?? o.color ?? INK;
    const t0 = times[i];
    if (t >= t0) {
      const p = clamp((t - t0) / 0.22);
      const s = 0.6 + 0.4 * backOut(p);
      const dy = (1 - expoOut(p)) * -(o.size ?? 120) * 0.25;
      ctx.save();
      ctx.translate(cx + widths[i] / 2, y + dy);
      ctx.scale(s, s);
      ctx.fillStyle = col;
      ctx.textAlign = 'center';
      ctx.fillText(ch, 0, 0);
      ctx.restore();
    }
    cx += widths[i];
  });
  return total;
}
// hairline reading attached to the thing it measures (mono)
function reading(str, ax, ay, lx, ly, t, t0, o = {}) {
  if (t < t0) return;
  const p = expoOut((t - t0) / 0.35);
  const col = o.color ?? INK;
  ctx.strokeStyle = col; ctx.lineWidth = (o.lw ?? 2) / Z; ctx.globalAlpha = o.alpha ?? 1;
  ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(lerp(ax, lx, p), lerp(ay, ly, p)); ctx.stroke();
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(ax, ay, 5 / Z, 0, 7); ctx.fill();
  ctx.globalAlpha = 1;
  const n = Math.floor(clamp((t - t0 - 0.12) * 30, 0, str.length));
  if (n > 0) {
    font(UI, (o.size ?? 38) / Z, 700);
    ctx.textAlign = o.align ?? (lx >= ax ? 'left' : 'right'); ctx.textBaseline = 'middle';
    ctx.fillStyle = col;
    ctx.fillText(str.slice(0, n), lx + (ctx.textAlign === 'left' ? 12 : -12) / Z, ly);
  }
}

// ------------------------------------------------------------------ paper grain (constant asset, seeded)
const grain = document.createElement('canvas');
grain.width = 540; grain.height = 960;
(() => {
  const g = grain.getContext('2d'), im = g.createImageData(540, 960), r = mulberry32(42);
  for (let i = 0; i < im.data.length; i += 4) {
    const v = r();
    im.data[i] = im.data[i + 1] = im.data[i + 2] = v < 0.5 ? 0 : 255;
    im.data[i + 3] = Math.floor(Math.pow(Math.abs(v - 0.5) * 2, 3) * 40);
  }
  g.putImageData(im, 0, 0);
})();
function paperBG() { screenCam(); ctx.fillStyle = PAPER; ctx.fillRect(0, 0, W, H); }
function darkBG() { screenCam(); ctx.fillStyle = DARK; ctx.fillRect(0, 0, W, H); }
function grainPass(alpha = 0.5) {
  screenCam();
  ctx.globalAlpha = alpha;
  const ox = Math.floor(hash(BT, 5) * 60), oy = Math.floor(hash(BT, 6) * 60);
  ctx.drawImage(grain, -ox, -oy, W * 1.1, H * 1.1);
  ctx.globalAlpha = 1;
}

// ------------------------------------------------------------------ radio field
// The Wi-Fi "light" is computed per pixel on a 1/3-res grid and tone-mapped to the one accent.
const FW = 360, FH = 640;
const fcv = document.createElement('canvas'); fcv.width = FW; fcv.height = FH;
const fctx = fcv.getContext('2d');
const fimg = fctx.createImageData(FW, FH);
const LUT = new Uint8ClampedArray(1024 * 3);
(() => {
  for (let i = 0; i < 1024; i++) {
    const v = i / 1023;                 // already tone-mapped 0..1
    let r, g, b;
    if (v < 0.62) {
      const k = Math.pow(v / 0.62, 1.15);
      r = lerp(DARK_RGB[0], ACC_RGB[0], k); g = lerp(DARK_RGB[1], ACC_RGB[1], k); b = lerp(DARK_RGB[2], ACC_RGB[2], k);
    } else {
      const k = (v - 0.62) / 0.38;
      r = lerp(ACC_RGB[0], HOT_RGB[0], k); g = lerp(ACC_RGB[1], HOT_RGB[1], k); b = lerp(ACC_RGB[2], HOT_RGB[2], k);
    }
    LUT[i * 3] = r; LUT[i * 3 + 1] = g; LUT[i * 3 + 2] = b;
  }
})();
// fn(wx, wy) -> intensity (>=0). Writes the tone-mapped field, then draws it full-frame.
function field(fn, o = {}) {
  const d = fimg.data, sx = W / FW, sy = H / FH, gain = o.gain ?? 1;
  let i = 0;
  for (let y = 0; y < FH; y++) {
    const wy = CAM.y + ((y + 0.5) * sy - H / 2) / CAM.z;
    for (let x = 0; x < FW; x++) {
      const wx = CAM.x + ((x + 0.5) * sx - W / 2) / CAM.z;
      const v = fn(wx, wy) * gain;
      const k = Math.min(1023, Math.floor((1 - Math.exp(-v)) * 1023)) * 3;
      d[i] = LUT[k]; d[i + 1] = LUT[k + 1]; d[i + 2] = LUT[k + 2]; d[i + 3] = 255;
      i += 4;
    }
  }
  fctx.putImageData(fimg, 0, 0);
  const saved = ctx.getTransform();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
  if (o.blur) ctx.filter = `blur(${o.blur}px)`;
  ctx.drawImage(fcv, 0, 0, W, H);
  ctx.filter = 'none';
  ctx.setTransform(saved);
}
// wave helpers. lam: wavelength (world), v: speed (world/s)
const TAU = Math.PI * 2;
function crest(r, t, lam, v, ph = 0) { const c = 0.5 + 0.5 * Math.cos(TAU * (r - v * t) / lam + ph); return c * c * c; }
// ring contrast fades out when the rings get too fine for the screen (level of detail)
function ringLOD(lam) { return clamp((lam * CAM.z - 14) / 26); }
function falloff(r, r0) { return 1 / (1 + r / r0); }
// beacon shells: pulses emitted at times tb (array), shell width w
function shells(r, t, tbs, v, w) {
  let s = 0;
  for (let k = 0; k < tbs.length; k++) {
    const age = t - tbs[k];
    if (age < 0 || age > 2.2) continue;
    const dr = (r - v * age) / w;
    if (dr > -4 && dr < 4) s += Math.exp(-dr * dr) * (1 - age / 2.2);
  }
  return s;
}

// ------------------------------------------------------------------ vision-switch front (the film's native move)
function front(t, t0, d = 0.9, dir = 1) {
  const p = ease((t - t0) / d);
  return dir > 0 ? lerp(-60, W + 60, p) : lerp(W + 60, -60, p);
}
function seam(x) {
  screenCam();
  const g = ctx.createLinearGradient(x - 70, 0, x + 6, 0);
  g.addColorStop(0, 'rgba(255,106,26,0)'); g.addColorStop(0.85, 'rgba(255,106,26,0.35)'); g.addColorStop(1, 'rgba(255,217,184,0.9)');
  ctx.fillStyle = g; ctx.fillRect(x - 70, 0, 76, H);
  ctx.fillStyle = HOT; ctx.fillRect(x - 1.5, 0, 3, H);
}

// draw into another canvas with the same helpers
function renderTo(canvas, fn) {
  const saved = ctx, savedCam = CAM, savedZ = Z;
  ctx = canvas.getContext('2d');
  fn();
  ctx = saved; CAM = savedCam; Z = savedZ;
  ctx.setTransform(Z, 0, 0, Z, W / 2 - CAM.x * Z, H / 2 - CAM.y * Z);
}
const OFF = document.createElement('canvas'); OFF.width = W; OFF.height = H;

// cheap deterministic blur: halve down a mip chain, then upsample back up it (no CSS filter)
const MIP = [], UPB = [];
for (let k = 1; k <= 7; k++) {
  for (const arr of [MIP, UPB]) { const c = document.createElement('canvas'); c.width = Math.max(2, Math.round(W / 2 ** k)); c.height = Math.max(2, Math.round(H / 2 ** k)); arr.push(c); }
}
function mipDown(src, n) {
  let prev = src;
  for (let i = 0; i < n; i++) {
    const g = MIP[i].getContext('2d'); g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
    g.clearRect(0, 0, MIP[i].width, MIP[i].height); g.drawImage(prev, 0, 0, MIP[i].width, MIP[i].height); prev = MIP[i];
  }
}
function mipUp(n) {          // returns a canvas holding level n, upsampled back to half resolution
  let cur = MIP[n - 1];
  for (let i = n - 2; i >= 0; i--) {
    const g = UPB[i].getContext('2d'); g.imageSmoothingEnabled = true; g.imageSmoothingQuality = 'high';
    g.clearRect(0, 0, UPB[i].width, UPB[i].height); g.drawImage(cur, 0, 0, UPB[i].width, UPB[i].height); cur = UPB[i];
  }
  return cur;
}
function drawBlurred(src, level, x = 0, y = 0, w = W, h = H) {
  level = clamp(level, 0, 7);
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
  const n = Math.floor(level), f = level - n;
  if (n + (f > 0 ? 1 : 0) > 0) mipDown(src, Math.min(7, n + 1));
  if (n === 0) ctx.drawImage(src, x, y, w, h); else ctx.drawImage(mipUp(n), x, y, w, h);
  if (f > 0 && n < 7) {
    const up = mipUp(n + 1);
    ctx.globalAlpha = f; ctx.drawImage(up, x, y, w, h); ctx.globalAlpha = 1;
  }
}
