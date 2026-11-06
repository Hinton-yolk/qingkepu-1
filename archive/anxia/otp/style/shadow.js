// Style test A+C: 皮影戏 · the verification code as a first-person puppet. Canvas 2D, seeded, three frames.
'use strict';
const W = 1080, H = 1920, TAU = Math.PI * 2;
const cv = document.getElementById('c'); cv.width = W; cv.height = H; const ctx = cv.getContext('2d');
function mulberry32(a) { return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const SERIF = '"Noto Serif CJK SC"', SANS = '"Noto Sans CJK SC"';
const P = { ink: '#2A140B', red: '#B8331E', redL: '#D9573A', blue: '#1E4A78', blueL: '#3A6EA5', green: '#3D7A36', ochre: '#C2862A', light: '#FFE4B0', wood: '#3A1F12' };

// ---------- the screen: backlit parchment
const FIB = (() => { const c = document.createElement('canvas'); c.width = 540; c.height = 960; const g = c.getContext('2d'), r = mulberry32(11), im = g.createImageData(540, 960);
  for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (r() - .5) * 40; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; } g.putImageData(im, 0, 0);
  g.globalAlpha = .35; for (let i = 0; i < 2600; i++) { const x = r() * 540, y = r() * 960, a = r() * TAU, l = 4 + r() * 18; g.strokeStyle = r() < .5 ? '#fff' : '#000'; g.lineWidth = .5; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a + .5) * l * .5, y + Math.sin(a + .5) * l * .5, x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke(); } return c; })();
function screen(x0, y0, x1, y1, hot = [W / 2, H * .46], o = {}) {
  ctx.save(); ctx.beginPath(); ctx.rect(x0, y0, x1 - x0, y1 - y0); ctx.clip();
  const g = ctx.createRadialGradient(hot[0], hot[1], 40, hot[0], hot[1], Math.max(x1 - x0, y1 - y0) * .8);
  g.addColorStop(0, '#FFF2D2'); g.addColorStop(.35, '#F8D69A'); g.addColorStop(.75, '#D99A4E'); g.addColorStop(1, '#7A3E16'); ctx.fillStyle = g; ctx.fillRect(x0, y0, x1 - x0, y1 - y0);
  ctx.globalCompositeOperation = 'soft-light'; ctx.globalAlpha = .55; ctx.drawImage(FIB, x0, y0, x1 - x0, y1 - y0); ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  ctx.strokeStyle = 'rgba(120,60,20,.12)'; ctx.lineWidth = 3; for (let i = 1; i < 4; i++) { ctx.beginPath(); ctx.moveTo(x0 + (x1 - x0) * i / 4 + Math.sin(i) * 10, y0); ctx.lineTo(x0 + (x1 - x0) * i / 4 - Math.sin(i) * 14, y1); ctx.stroke(); }      // soft folds
  ctx.restore();
}
function vignette(a = .55) { const g = ctx.createRadialGradient(W / 2, H * .45, H * .3, W / 2, H * .5, H * .78); g.addColorStop(0, 'rgba(30,10,0,0)'); g.addColorStop(1, `rgba(30,10,0,${a})`); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); }

// ---------- leather: a translucent coloured piece with a dark outline and cut-out patterns that let the light through
let BACKSTAGE = false;
function leather(path, col, o = {}) {
  ctx.save(); path(); ctx.globalAlpha = o.alpha ?? .92;
  if (!BACKSTAGE && !o.opaque) ctx.globalCompositeOperation = 'multiply';
  const g = ctx.createLinearGradient(0, -200, 0, 200); g.addColorStop(0, o.light ?? col); g.addColorStop(1, col); ctx.fillStyle = o.flat ? col : g; ctx.fill();
  ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1; ctx.lineJoin = 'round'; ctx.strokeStyle = P.ink; ctx.lineWidth = o.lw ?? 6; ctx.stroke(); ctx.restore();
}
// carved scrolls: thin bright cuts that make the leather look like lace
function scrolls(cx, cy, w, h, seed, o = {}) {
  const r = mulberry32(seed); ctx.save(); ctx.strokeStyle = o.col ?? 'rgba(255,240,200,.95)'; ctx.lineWidth = o.lw ?? 3.2; ctx.lineCap = 'round';
  for (let i = 0; i < (o.n ?? 26); i++) { const x = cx + (r() - .5) * w, y = cy + (r() - .5) * h, rr = 8 + r() * 12, a = r() * TAU; ctx.beginPath(); ctx.arc(x, y, rr, a, a + 3.6); ctx.stroke(); ctx.beginPath(); ctx.arc(x + Math.cos(a + 3.6) * rr * .55, y + Math.sin(a + 3.6) * rr * .55, rr * .45, a + 3.6, a + 6.6); ctx.stroke(); }
  ctx.restore();
}
function holes(cx, cy, w, h, seed, o = {}) {      // a carved pattern: rows of small crescents and dots
  const r = mulberry32(seed); ctx.save(); ctx.fillStyle = o.col ?? 'rgba(255,236,190,.9)';
  for (let y = cy - h / 2 + 14; y < cy + h / 2 - 8; y += o.step ?? 26) for (let x = cx - w / 2 + 14 + ((y / (o.step ?? 26)) % 2) * 12; x < cx + w / 2 - 8; x += o.step ?? 26) {
    const k = r(); ctx.beginPath();
    if (k < .5) { ctx.arc(x, y, o.dot ?? 3.6, 0, TAU); ctx.fill(); }
    else { ctx.arc(x, y, 7, .2 * Math.PI, .8 * Math.PI); ctx.arc(x, y - 3, 6, .78 * Math.PI, .22 * Math.PI, true); ctx.fill(); }
  }
  ctx.restore();
}
function rivet(x, y, r = 7) { ctx.fillStyle = P.ink; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); ctx.fillStyle = 'rgba(255,220,160,.6)'; ctx.beginPath(); ctx.arc(x - r * .25, y - r * .25, r * .35, 0, TAU); ctx.fill(); }
function stick(x, y, x2, y2, blur = 2) { ctx.save(); ctx.filter = `blur(${blur}px)`; ctx.strokeStyle = 'rgba(42,20,11,.85)'; ctx.lineWidth = 7; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x2, y2); ctx.stroke(); ctx.restore(); }

// ---------- the protagonist: 836592, a little messenger with a token for a body
function codePuppet(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(o.rot ?? 0);
  // legs and boots
  leather(() => { ctx.beginPath(); ctx.moveTo(-60, 250); ctx.lineTo(-30, 250); ctx.lineTo(-24, 360); ctx.lineTo(-70, 372); ctx.lineTo(-74, 352); ctx.lineTo(-52, 344); ctx.closePath(); }, P.ink, { flat: true, alpha: .95 });
  leather(() => { ctx.beginPath(); ctx.moveTo(30, 250); ctx.lineTo(60, 250); ctx.lineTo(56, 344); ctx.lineTo(82, 352); ctx.lineTo(78, 372); ctx.lineTo(26, 360); ctx.closePath(); }, P.ink, { flat: true, alpha: .95 });
  // the token body
  const body = () => { ctx.beginPath(); ctx.moveTo(-110, -60); ctx.quadraticCurveTo(-110, -150, 0, -160); ctx.quadraticCurveTo(110, -150, 110, -60); ctx.lineTo(118, 250); ctx.lineTo(-118, 250); ctx.closePath(); };
  leather(body, P.red, { light: P.redL });
  ctx.save(); body(); ctx.clip(); holes(0, 200, 230, 90, 3, { step: 22, dot: 3 }); ctx.restore();
  ctx.strokeStyle = 'rgba(255,230,180,.85)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(-90, -70); ctx.quadraticCurveTo(-90, -130, 0, -138); ctx.quadraticCurveTo(90, -130, 90, -70); ctx.lineTo(96, 150); ctx.lineTo(-96, 150); ctx.closePath(); ctx.stroke();
  // the six digits are cut right through the leather: they glow with the light behind
  ctx.font = `900 92px ${SERIF}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#FFF0CC';
  ['836', '592'].forEach((r, i) => ctx.fillText(r, 0, -40 + i * 110));
  ctx.save(); body(); ctx.clip(); scrolls(0, 222, 210, 40, 12, { n: 12, lw: 2.6 }); ctx.restore();
  // arms, held out to the sides with flared sleeves
  const armL = o.armL ?? -.9, armR = o.armR ?? .9;
  for (const [sx, a] of [[-112, armL], [112, armR]]) {
    ctx.save(); ctx.translate(sx, -40); ctx.rotate(a);
    leather(() => { ctx.beginPath(); ctx.moveTo(-12, 0); ctx.lineTo(12, 0); ctx.lineTo(26, 120); ctx.lineTo(-26, 120); ctx.closePath(); }, P.ochre, { lw: 5 });
    ctx.save(); ctx.beginPath(); ctx.moveTo(-12, 0); ctx.lineTo(12, 0); ctx.lineTo(26, 120); ctx.lineTo(-26, 120); ctx.closePath(); ctx.clip(); holes(0, 60, 40, 110, 40, { step: 16, dot: 2.6 }); ctx.restore();
    ctx.translate(0, 116); ctx.rotate(a * .4); leather(() => { ctx.beginPath(); ctx.roundRect(-9, 0, 18, 80, 9); }, P.ochre, { lw: 4 });
    leather(() => { ctx.beginPath(); ctx.ellipse(0, 88, 13, 16, 0, 0, TAU); }, '#F0D2A8', { lw: 4 });
    rivet(0, 0, 6); ctx.restore(); rivet(sx, -40, 7);
  }
  // the head: a hollow-carved profile (only its lines), a messenger's cap with two wings
  ctx.save(); ctx.translate(0, -212);
  ctx.strokeStyle = P.ink; ctx.lineWidth = 6; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(-36, -40); ctx.quadraticCurveTo(-60, 0, -40, 44); ctx.quadraticCurveTo(-10, 66, 30, 54); ctx.lineTo(40, 34); ctx.lineTo(50, 30); ctx.lineTo(46, 20); ctx.lineTo(54, 14); ctx.lineTo(66, 2); ctx.lineTo(52, -6); ctx.lineTo(46, -40); ctx.stroke();
  ctx.lineWidth = 4.5; ctx.beginPath(); ctx.moveTo(10, -16); ctx.quadraticCurveTo(28, -24, 44, -14); ctx.stroke(); ctx.beginPath(); ctx.moveTo(14, -6); ctx.quadraticCurveTo(28, -12, 40, -4); ctx.quadraticCurveTo(28, 2, 14, -6); ctx.stroke();
  ctx.beginPath(); ctx.arc(-12, 6, 10, .3, 5.6); ctx.stroke();
  leather(() => { ctx.beginPath(); ctx.moveTo(-46, -36); ctx.quadraticCurveTo(-36, -96, 14, -96); ctx.quadraticCurveTo(54, -92, 50, -38); ctx.closePath(); }, P.ink, { flat: true, alpha: .95, lw: 4, opaque: true });
  for (const sgn of [-1, 1]) { ctx.save(); ctx.translate(sgn < 0 ? -80 : 84, -70); ctx.rotate(sgn * .25); leather(() => { ctx.beginPath(); ctx.ellipse(0, 0, 36, 13, 0, 0, TAU); }, P.ink, { flat: true, alpha: .95, lw: 3, opaque: true }); ctx.fillStyle = 'rgba(255,236,190,.9)'; ctx.beginPath(); ctx.ellipse(0, 0, 20, 4, 0, 0, TAU); ctx.fill(); ctx.restore(); }
  ctx.restore();
  ctx.restore();
  ctx.restore();
}
// your shadow: a soft profile holding a phone to the ear (a real shadow, not a puppet)
function yourShadow(x, y, s, blur = 6) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.filter = `blur(${blur}px)`; ctx.fillStyle = 'rgba(42,22,12,.82)';
  ctx.beginPath(); ctx.moveTo(-120, 420); ctx.quadraticCurveTo(-140, 220, -60, 160); ctx.lineTo(-40, 110); ctx.quadraticCurveTo(-90, 80, -88, 10); ctx.quadraticCurveTo(-84, -80, 0, -96); ctx.quadraticCurveTo(70, -100, 84, -30); ctx.lineTo(108, 6); ctx.lineTo(88, 20); ctx.quadraticCurveTo(90, 70, 50, 90); ctx.lineTo(60, 150); ctx.quadraticCurveTo(170, 200, 180, 420); ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.roundRect(40, -60, 38, 80, 8); ctx.fill();      // the phone at the ear
  ctx.beginPath(); ctx.moveTo(-10, 170); ctx.quadraticCurveTo(20, 60, 58, 10); ctx.lineTo(82, 30); ctx.quadraticCurveTo(50, 90, 30, 190); ctx.closePath(); ctx.fill();
  ctx.restore();
}
// the "客服": a smiling mask over a sharp face, a headset, robes in indigo
function agentPuppet(x, y, s, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  const robe = () => { ctx.beginPath(); ctx.moveTo(-70, -40); ctx.lineTo(70, -40); ctx.lineTo(120, 300); ctx.lineTo(-120, 300); ctx.closePath(); };
  leather(robe, P.blue, { light: P.blueL }); ctx.save(); robe(); ctx.clip(); holes(0, 150, 220, 260, 8, { step: 30, dot: 4 }); ctx.restore();
  ctx.save(); ctx.translate(0, -110);
  leather(() => { ctx.beginPath(); ctx.moveTo(-36, 60); ctx.quadraticCurveTo(-60, -10, -28, -56); ctx.quadraticCurveTo(14, -74, 44, -44); ctx.lineTo(60, -14); ctx.lineTo(80, -4); ctx.lineTo(56, 10); ctx.quadraticCurveTo(46, 50, 0, 70); ctx.closePath(); }, '#8A8F98', { lw: 5, alpha: .95 });
  // the smiling mask, held a little in front of the face
  leather(() => { ctx.beginPath(); ctx.ellipse(36, 0, 42, 52, .1, 0, TAU); }, '#F7E6C8', { lw: 4, alpha: .97, opaque: true });
  ctx.strokeStyle = P.ink; ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(24, -12, 9, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); ctx.beginPath(); ctx.arc(52, -12, 9, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); ctx.beginPath(); ctx.arc(38, 16, 20, .15 * Math.PI, .85 * Math.PI); ctx.stroke();
  ctx.strokeStyle = P.ink; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(0, -10, 62, Math.PI * 1.05, Math.PI * 1.95); ctx.stroke(); ctx.beginPath(); ctx.moveTo(-58, 2); ctx.quadraticCurveTo(-30, 50, 20, 44); ctx.stroke(); ctx.fillStyle = P.ink; ctx.beginPath(); ctx.arc(22, 44, 8, 0, TAU); ctx.fill();      // headset
  ctx.restore(); ctx.restore();
}
function phoneProp(x, y, s, text, rot = 0) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s); ctx.fillStyle = '#18161C'; ctx.beginPath(); ctx.roundRect(-60, -120, 120, 240, 16); ctx.fill(); const g = ctx.createLinearGradient(0, -110, 0, 110); g.addColorStop(0, '#DDEBFF'); g.addColorStop(1, '#9CC2F2'); ctx.fillStyle = g; ctx.beginPath(); ctx.roundRect(-52, -110, 104, 220, 10); ctx.fill(); ctx.fillStyle = P.red; ctx.beginPath(); ctx.roundRect(-40, 52, 80, 34, 17); ctx.fill(); ctx.font = `700 18px ${SANS}`; ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(text, 0, 69); ctx.font = `900 30px ${SERIF}`; ctx.fillStyle = '#1E2A40'; ctx.fillText('¥5,000', 0, -20); ctx.restore(); }
function seal(x, y, sz, txt, rot = -.06) { ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.fillStyle = '#B5281C'; ctx.beginPath(); ctx.roundRect(-sz / 2, -sz / 2, sz, sz, sz * .08); ctx.fill(); ctx.strokeStyle = 'rgba(255,230,210,.85)'; ctx.lineWidth = sz * .04; ctx.strokeRect(-sz * .4, -sz * .4, sz * .8, sz * .8); ctx.font = `900 ${sz * .34}px ${SERIF}`; ctx.fillStyle = '#FFE9DC'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(txt, 0, sz * .02); ctx.restore(); }
function ink(lines, x, y, sz, o = {}) { ctx.save(); ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic'; lines.forEach((ln, i) => { let cx = x; for (const [s, col] of ln) { ctx.font = `900 ${sz}px ${SERIF}`; ctx.fillStyle = col ?? (o.col ?? P.ink); if (o.glow) { ctx.shadowColor = o.glow; ctx.shadowBlur = 18; } ctx.fillText(s, cx, y + i * sz * 1.22); cx += ctx.measureText(s).width; } }); ctx.restore(); }
function cloudProp(y, col, seed) {      // a traditional carved cloud band, pressed to the bottom of the screen
  const r = mulberry32(seed); const path = () => { ctx.beginPath(); ctx.moveTo(40, y + 120); for (let x = 40; x <= W - 40; x += 90) { const h = 40 + r() * 50; ctx.quadraticCurveTo(x + 20, y - h, x + 45, y); ctx.quadraticCurveTo(x + 70, y - h * .7, x + 90, y + 10); } ctx.lineTo(W - 40, y + 120); ctx.closePath(); };
  leather(path, col, { lw: 5 }); ctx.save(); path(); ctx.clip(); scrolls(W / 2, y + 50, W - 120, 80, seed + 1, { n: 30, lw: 3 }); holes(W / 2, y + 90, W - 100, 40, seed + 2, { step: 22, dot: 3 }); ctx.restore();
}
function gong(x, y, r) { const g = ctx.createRadialGradient(x - r * .3, y - r * .3, r * .1, x, y, r); g.addColorStop(0, '#F3C86A'); g.addColorStop(.6, '#B9822C'); g.addColorStop(1, '#6E4515'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); ctx.strokeStyle = 'rgba(60,30,10,.6)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(x, y, r * .55, 0, TAU); ctx.stroke(); ctx.strokeStyle = '#8B1E12'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(x, y - r); ctx.lineTo(x, y - r - 140); ctx.stroke(); }

// ---------- frames
const FR = [
  () => {      // 1 · the first frame: the code introduces itself; a red seal counts down
    ctx.fillStyle = P.wood; ctx.fillRect(0, 0, W, H);
    screen(40, 40, W - 40, H - 220, [W * .52, H * .5]);
    stick(470, 1010, 380, 1900, 3); stick(330, 1180, 230, 1900, 3); stick(760, 1150, 900, 1900, 3);
    cloudProp(H - 340, P.green, 21);
    codePuppet(560, 1080, 1.35, { armL: .95, armR: -.55 });
    ink([[['我只能活', null], ['5 分钟', P.red], ['。', null]]], 90, 300, 112);
    ink([[['我叫 836592。', null]]], 92, 440, 64, { col: 'rgba(42,20,11,.85)' });
    seal(930, 250, 150, '4:59');
    ctx.fillStyle = P.wood; ctx.fillRect(0, H - 220, W, 220); ctx.fillStyle = '#5A3220'; ctx.fillRect(0, H - 226, W, 10);
    gong(150, H - 120, 78);
    ctx.font = `700 34px ${SANS}`; ctx.fillStyle = 'rgba(255,220,170,.75)'; ctx.textAlign = 'right'; ctx.fillText('你按下去之后 · 验证码', W - 60, H - 100);
    vignette(.5);
  },
  () => {      // 2 · 幕前 / 幕后: in front, a polite 客服; behind, someone holds the sticks and another phone
    ctx.fillStyle = '#120806'; ctx.fillRect(0, 0, W, H);
    // the front: the screen, the 客服's coloured shadow, a speech scroll
    screen(40, 40, W - 40, 1010, [W * .55, 560]);
    stick(560, 820, 470, 1010, 3); stick(700, 760, 820, 1010, 3);
    agentPuppet(600, 600, 1.05);
    ctx.save(); ctx.translate(210, 560); ctx.rotate(-.04); ctx.fillStyle = 'rgba(255,248,230,.92)'; ctx.beginPath(); ctx.roundRect(-150, -66, 300, 132, 22); ctx.fill(); ctx.strokeStyle = P.ink; ctx.lineWidth = 4; ctx.stroke();
    ctx.font = `900 40px ${SERIF}`; ctx.fillStyle = P.ink; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('您好，我是客服', 0, -20); ctx.fillText('给您退款～', 0, 30); ctx.restore();
    ink([[['幕前：', null], ['「我是客服」', P.red]]], 80, 180, 84);
    // the edge of the screen
    ctx.fillStyle = '#4A2A18'; ctx.fillRect(0, 1010, W, 26);
    // behind: dark, the lamp's glow, the operator from behind holding the sticks up to the screen, and a phone
    BACKSTAGE = true;
    const lg = ctx.createRadialGradient(W * .5, 1060, 10, W * .5, 1060, 760); lg.addColorStop(0, 'rgba(255,190,110,.55)'); lg.addColorStop(1, 'rgba(255,150,70,0)'); ctx.fillStyle = lg; ctx.fillRect(0, 1036, W, H - 1036);
    ctx.fillStyle = '#FFD58A'; ctx.beginPath(); ctx.ellipse(W * .5, 1080, 20, 28, 0, 0, TAU); ctx.fill();
    // the sticks run from his hands up through the edge to the puppet in front
    ctx.strokeStyle = '#2A1A10'; ctx.lineWidth = 9; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(470, 1010); ctx.lineTo(380, 1520); ctx.moveTo(820, 1010); ctx.lineTo(700, 1500); ctx.stroke();
    // the operator, from behind: head, shoulders, raised arms
    ctx.fillStyle = '#1C0F09'; ctx.beginPath(); ctx.ellipse(540, 1560, 96, 112, 0, 0, TAU); ctx.fill();
    ctx.beginPath(); ctx.moveTo(250, H); ctx.quadraticCurveTo(300, 1660, 540, 1650); ctx.quadraticCurveTo(780, 1660, 830, H); ctx.closePath(); ctx.fill();
    ctx.lineWidth = 64; ctx.strokeStyle = '#1C0F09'; ctx.beginPath(); ctx.moveTo(360, 1720); ctx.quadraticCurveTo(320, 1610, 378, 1530); ctx.stroke(); ctx.beginPath(); ctx.moveTo(720, 1720); ctx.quadraticCurveTo(800, 1640, 860, 1610); ctx.stroke();
    ctx.strokeStyle = 'rgba(255,190,110,.35)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(540, 1560, 98, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke();      // rim light
    phoneProp(880, 1560, 1.35, '确认转账', -.12);
    ctx.save(); ctx.translate(880, 1560); ctx.rotate(-.12); ctx.scale(1.35, 1.35); ctx.font = `700 16px ${SANS}`; ctx.fillStyle = '#1E2A40'; ctx.textAlign = 'center'; ctx.fillText('验证码 _ _ _ _ _ _', 0, 22); ctx.restore();
    ink([[['幕后：另一台手机，', null]], [['正等着你的验证码。', null]]], 70, 1180, 66, { col: '#F6E2C0' });
    BACKSTAGE = false;
    vignette(.35);
  },
  () => {      // 3 · the end: the code passes through the screen and seals the stranger's transfer
    ctx.fillStyle = P.wood; ctx.fillRect(0, 0, W, H);
    screen(40, 40, W - 40, H - 220, [W * .5, H * .42]);
    // coins (old cash cut-outs) streaming away to the right
    for (let i = 0; i < 9; i++) { const x = 560 + i * 60, y = 760 + Math.sin(i * .9) * 70 - i * 18; ctx.save(); ctx.translate(x, y); ctx.rotate(i * .4); leather(() => { ctx.beginPath(); ctx.arc(0, 0, 34, 0, TAU); }, P.ochre, { lw: 4 }); ctx.fillStyle = '#FFE8B8'; ctx.fillRect(-9, -9, 18, 18); ctx.restore(); }
    cloudProp(H - 340, P.blue, 22);
    // the seal stamped across the screen
    ctx.save(); ctx.globalAlpha = .9; seal(540, 900, 380, '确认', -.08); ctx.restore();
    // the little code, bowing, its digits coming loose
    codePuppet(260, 1250, .9, { armL: .5, armR: -1.3, rot: .18 });
    const r = mulberry32(5); ctx.font = `900 64px ${SERIF}`; ctx.fillStyle = '#FFF0CC'; ['8', '3', '6', '5', '9', '2'].forEach((d, i) => { ctx.save(); ctx.translate(420 + i * 70, 1320 - i * 40 + r() * 40); ctx.rotate((r() - .5) * .8); ctx.strokeStyle = P.ink; ctx.lineWidth = 8; ctx.strokeText(d, 0, 0); ctx.fillText(d, 0, 0); ctx.restore(); });
    ink([[['我替一个陌生人，', null]], [['按下了', null], ['确认', P.red], ['。', null]]], 90, 290, 100);
    seal(930, 250, 150, '0:00');
    ctx.fillStyle = P.wood; ctx.fillRect(0, H - 220, W, 220); ctx.fillStyle = '#5A3220'; ctx.fillRect(0, H - 226, W, 10); gong(150, H - 120, 78);
    vignette(.5);
  },
];
window.seek = function (i) { ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.filter = 'none'; FR[i | 0](); return true; };
window.ready = Promise.all([`900 100px ${SERIF}`, `700 34px ${SANS}`].map(f => document.fonts.load(f)));
window.DURATION = 3; window.FPS = 1;
