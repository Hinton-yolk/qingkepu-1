// 如果眼睛能看见 Wi-Fi · 高岛平团地 — one continuous take over a 1:1000 white model.
// render(t) is a pure function of time: every state below is computed from t and timeline.json; nothing is carried between frames.
import * as THREE from 'three';
import { makeStudio, ACC, HOT } from './studio.js';

const QS = new URLSearchParams(location.search);
const DRAFT = QS.has('draft');
const W = innerWidth, H = innerHeight;
const [M, ST, TL] = await Promise.all(['data/A/model.json', 'data/A/stats.json', 'timeline.json'].map(u => fetch(u).then(r => r.json())));
const T = TL.t, CUES = TL.cues;
const S = makeStudio(W, H, M, DRAFT ? { pr: 1, ssaa: 1, shadow: 2048 } : { pr: +(QS.get('pr') || 1), ssaa: +(QS.get('ssaa') || 2), shadow: 4096 });
const { U, camera, post, renderer, house, hemi, scene } = S;
S.build(await new THREE.TextureLoader().loadAsync('data/A/glow.png'));
{ // depth of field: fewer gather taps (software WebGL); the supersampled frame is averaged down, which hides the sparser spiral
  const gm = post.dof.gat.material, taps = +(QS.get('taps') || 48);
  gm.fragmentShader = gm.fragmentShader.replace('const int N = 96;', `const int N = ${taps};`); gm.needsUpdate = true;
}

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ss = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const lerp = (a, b, k) => a + (b - a) * k;
const fmt = n => n.toLocaleString('en-US');
const easeIn = x => { x = clamp(x); return x * x * x; };
const easeOut = x => { x = clamp(x); return 1 - (1 - x) ** 3; };

// ------------------------------------------------------------------ the slab's frame: c centre, u long axis, n facade normal
const PICK = ST.pick.i, N1 = 32, N2 = 34;          // 隔壁 / 再隔壁: the next two slabs out along the facade normal (FACTS.md)
const partsOf = bi => M.p.filter(p => p[0] === bi);
function axisOf(bi) {
  const pts = partsOf(bi)[0][2][0]; const n = pts.length;
  const cx = pts.reduce((s, p) => s + p[0], 0) / n, cz = pts.reduce((s, p) => s + p[1], 0) / n;
  let sxx = 0, szz = 0, sxz = 0; for (const [x, z] of pts) { sxx += (x - cx) ** 2; szz += (z - cz) ** 2; sxz += (x - cx) * (z - cz); }
  const a = .5 * Math.atan2(2 * sxz, sxx - szz);
  return { c: [cx, cz], u: [Math.cos(a), Math.sin(a)], pts };
}
const A = axisOf(PICK), c = A.c, u = A.u, n = [-u[1], u[0]];
const hm = ST.pick.h / 1000, flH = hm / ST.pick.floors;
const S3 = (uo, no, y) => [c[0] + u[0] * uo + n[0] * no, y, c[1] + u[1] * uo + n[1] * no];   // slab coords → world
const halfW = -Math.min(...A.pts.map(([x, z]) => (x - c[0]) * n[0] + (z - c[1]) * n[1]));     // the −n facade, model metres
const roofTop = bi => Math.max(...partsOf(bi).map(p => p[1]));
const centre = bi => { const p = partsOf(bi)[0][2][0]; return [p.reduce((s, q) => s + q[0], 0) / p.length, p.reduce((s, q) => s + q[1], 0) / p.length]; };

// the seed window: the −n facade, floor 9, a little left of the middle (a window centre on the shader's grid)
const fN = [-n[0], -n[1]], tg = [-fN[1], fN[0]];
const seedAlong0 = (c[0] - u[0] * .006 - n[0] * halfW) * tg[0] + (c[1] - u[1] * .006 - n[1] * halfW) * tg[1];
const seedAlong = (Math.floor(seedAlong0 / .0065) + .5) * .0065, seedY = 8.5 * flH;
const base = [c[0] - n[0] * halfW, c[1] - n[1] * halfW], bAlong = base[0] * tg[0] + base[1] * tg[1];
const seed = [base[0] + tg[0] * (seedAlong - bAlong), seedY, base[1] + tg[1] * (seedAlong - bAlong)];
// 「我在这儿」: a window three bays right of the seed, two floors up
const here = [seed[0] + tg[0] * .0065 * 3, seedY + flH * 2, seed[2] + tg[1] * .0065 * 3];
U.uSeed.value.set(...seed); U.uHereP.value.set(...here);
const toSlab = ([x, y, z]) => [(x - c[0]) * u[0] + (z - c[1]) * u[1], (x - c[0]) * n[0] + (z - c[1]) * n[1], y];
const hereS = toSlab(here);
const seedCell = Math.floor(seedAlong / .0065);
U.uSeedN.value.set(fN[0], fN[1]); U.uSeedCell.value.set(seedCell, 8); U.uHereCell.value.set(seedCell + 3, 10);
U.uPick.value = PICK; U.uPickC.value.set(c[0], c[1]);
U.uN1.value = N1; U.uN2.value = N2; U.uN1T.value = T.n1; U.uN2T.value = T.n2;
U.uSpreadT.value = T.spread; U.uSpreadV.value = 128;
const cN1 = centre(N1), cN2 = centre(N2);
U.uRS.value[0].set(c[0], c[1], T.spill); U.uRS.value[1].set(cN1[0], cN1[1], T.n1 + .3); U.uRS.value[2].set(cN2[0], cN2[1], T.n2 + .3);
U.uProjPos.value.set(...S3(.1, -.9, 1.1));
house.position.set(...S3(-.6, 1.6, 1.5)); house.target.position.set(c[0], 0, c[1]); house.target.updateMatrixWorld();
renderer.shadowMap.needsUpdate = true;

// ------------------------------------------------------------------ the camera: one take, keys in slab coordinates
// [t, cam(u, n, y), target(u, n, y), fov, aperture]
const KEYS = [
  [0.0,  [-.016, -.024, .029], [-.006, -halfW, seedY], 30, 3.2],
  [3.5,  [-.045, -.044, .052], [.000, -halfW, .024], 30, 2.8],
  [8.5,  [.140, -.330, .300], [.000, -.012, .022], 30, 1.8],
  [13.5, [-.120, -.360, .260], [-.004, -.012, .022], 30, 1.8],
  [17.5, [hereS[0] + .040, -.042, .043], [hereS[0] - .004, hereS[1], hereS[2] + .002], 30, 2.6],
  [20.0, [.020, -.040, .030], [-.020, -.010, .006], 32, 2.2],
  [22.5, [.075, -.040, .048], [.000, -.024, .000], 34, 1.9],
  [24.5, [.030, -.030, .125], [.000, .045, .020], 32, 1.6],
  [26.5, [.160, -.330, .290], [.010, .060, .018], 30, 1.6],
  [31.0, [.300, -.720, .780], [.010, .030, .000], 30, 1.2],
  [33.5, [.120, -.640, .520], [.000, .030, .000], 30, 1.3],
  [36.5, [-.150, -.300, .110], [.020, .050, .015], 30, 2.0],
  [40.0, [-.260, -.420, .260], [.020, .040, .010], 30, 1.6],
  [46.0, [-.800, -1.40, 1.650], [.000, .020, -.060], 30, 1.0],
];
function hermite(t, get) {
  let i = 0; while (i < KEYS.length - 2 && t > KEYS[i + 1][0]) i++;
  const k0 = KEYS[Math.max(0, i - 1)], k1 = KEYS[i], k2 = KEYS[i + 1], k3 = KEYS[Math.min(KEYS.length - 1, i + 2)];
  const h = k2[0] - k1[0], s = clamp((t - k1[0]) / h);
  const p1 = get(k1), p2 = get(k2);
  const m1 = p1.map((_, j) => (get(k2)[j] - get(k0)[j]) / (k2[0] - k0[0] || h) * h);
  const m2 = p1.map((_, j) => (get(k3)[j] - get(k1)[j]) / (k3[0] - k1[0] || h) * h);
  const s2 = s * s, s3 = s2 * s;
  return p1.map((_, j) => (2 * s3 - 3 * s2 + 1) * p1[j] + (s3 - 2 * s2 + s) * m1[j] + (-2 * s3 + 3 * s2) * p2[j] + (s3 - s2) * m2[j]);
}
const tgtV = new THREE.Vector3();
function placeCamera(t) {
  const cam = hermite(t, k => k[1]), tgt = hermite(t, k => k[2]);
  { // the first window sits exactly in the middle of the first frame (the key aims at the slab, the window snaps to its grid)
    const s0 = toSlab(seed), k = 1 - ss(t / 1.5);
    for (let j = 0; j < 3; j++) tgt[j] += (s0[j] - KEYS[0][2][j]) * k;
  }
  const [fov, aper] = hermite(t, k => [k[3], k[4]]);
  camera.position.set(...S3(...cam)); tgtV.set(...S3(...tgt)); camera.lookAt(tgtV);
  if (camera.fov !== fov) { camera.fov = fov; camera.updateProjectionMatrix(); }
  camera.updateMatrixWorld();
  post.dof.focus = camera.position.distanceTo(tgtV); post.dof.aper = aper; post.dof.maxCoc = QS.has('nodof') ? 0 : 14;
}
const proj = (x, y, z) => { const v = new THREE.Vector3(x, y, z).project(camera); return v.z < 1 ? [(v.x * .5 + .5) * W, (-v.y * .5 + .5) * H] : null; };

// ------------------------------------------------------------------ light state from t
function lightState(t) {
  // the opening: one window, then the facade catches outward from it and lands on 「会是这样」
  U.uCasc.value = t < .5 ? .5 : lerp(.5, 150, clamp((t - .5) / (T.cascade - .5)) ** 1.6);
  U.uCount.value = t < R[0].roll[0] ? -1 : easeOut((t - R[0].roll[0]) / (R[0].roll[1] - R[0].roll[0])) * (t < R[0].roll[1] + .6 ? 1 : 0) - (t >= R[0].roll[1] + .6 ? 1 : 0);
  U.uRate.value = 1 + ss((t - T.readout2) / .8) - ss((t - T.boom) / 1.2);
  U.uHereT.value = T.here;
  U.uHereDim.value = ss((t - (T.here - .5)) / .3) * (1 - ss((t - (T.here + .9)) / .4));
  U.uSpill.value = ss((t - T.spill) / 1.2);
  U.uRA.value.set(1, ss((t - T.n1) / .6), ss((t - T.n2) / .6));
  U.uGlow.value = ss((t - T.spread - .5) / 2.2);
  // house lights: dim key while the data is on; up slowly (1 s) when the data stops; cut fast (0.25 s) for the lamp
  const up = ss((t - T.lightsup) / 1.0) * (1 - ss((t - (T.lamp - .25)) / .25));
  house.intensity = lerp(.16, .62, up); hemi.intensity = lerp(.05, .16, up); scene.environmentIntensity = lerp(.1, .28, up);
  // the projector: off with the house lights (0.25 s), strikes with a short flicker at the lamp
  let p = 1 - ss((t - T.lightsup) / .25);
  if (t >= T.lamp) {
    const a = t - T.lamp;
    const fl = [1, 0, .7, .1, 1, .35, 1][Math.min(6, Math.floor(a / .055))];
    p = a < .385 ? fl * .9 : 1;
  }
  U.uProj.value = p;
}

// ------------------------------------------------------------------ the 2D layer: readouts (left third), pins, subtitles, end card
const ov = document.getElementById('ov'), g = ov.getContext('2d');
const DISPLAY = '"Inter Tight"', UI = '"Noto Sans Mono CJK SC"';
const TEXTS = [];
const reg = (id, text, x0, y0, x1, y1) => TEXTS.push({ id, text, x0: Math.round(x0), y0: Math.round(y0), x1: Math.round(x1), y1: Math.round(y1) });
const plate = (x, y, w, h, a = .62) => { g.fillStyle = `rgba(8,9,10,${a})`; g.fillRect(x, y, w, h); };
// a reveal is a wipe of light from the left (in) and back (out); nothing fades
function wipe(t, t0, t1, dIn = .4, dOut = .3) { return t < t0 || t > t1 ? 0 : Math.min(easeOut((t - t0) / dIn), easeOut((t1 - t) / dOut)); }

const R = [
  { id: 'r1', t0: T.readout1, t1: T.readout2 - .2, idx: '01 · 这一栋', fig: ST.pick.routers, roll: [T.readout1 + .5, T.count1], unit: '户',
    label: `≈ ${ST.pick.routers} 台路由器（估算）`, src: [`高岛平团地 · 东京板桥区 · 1:1000`, '数据：国土交通省 PLATEAU（CC BY 4.0）'] },
  { id: 'r2', t0: T.readout2, t1: T.spill - .2, idx: '02 · 信标', fig: 10, roll: [T.readout2 + .5, T.count2], unit: '次/秒', approx: true,
    label: '每台都在广播「我在这儿」', src: ['默认每 102.4 毫秒一次（IEEE 802.11）', '画面闪烁节奏为示意'] },
  { id: 'r3', t0: T.spill, t1: T.n1 - .3, idx: '03 · 穿墙', fig: 12.5, dec: 1, roll: [T.spill + .2, T.spill + 1.5], unit: '厘米',
    label: '2.4 GHz 的真实波长', src: ['画面上的环距已放大约 150 倍', '示意，不是实测'] },
  { id: 'r4', t0: T.spread, t1: T.lightsup, idx: '04 · 这一片', fig: ST.routers, roll: [T.spread + .3, T.all], unit: '台', legend: true,
    label: `路由器（估算）· 半径 ${ST.site.r} 米`, src: [`${ST.buildings} 栋楼 · 住宅约 ${fmt(Math.round(ST.homes / 100) * 100)} 户`, '数据：国土交通省 PLATEAU（CC BY 4.0）'] },
];
function drawReadout(r, t) {
  const k = wipe(t, r.t0, r.t1); if (k <= 0) return;
  const x = 64, y = 300, bw = 660;
  g.save(); g.beginPath(); g.rect(0, y - 100, bw * k, 560); g.clip();
  const bg = g.createLinearGradient(0, 0, bw, 0); bg.addColorStop(0, 'rgba(5,6,7,.62)'); bg.addColorStop(.7, 'rgba(5,6,7,.35)'); bg.addColorStop(1, 'rgba(5,6,7,0)');
  g.fillStyle = bg;
  for (let i = 0; i < 26; i++) { const a = i < 4 ? i / 4 : i > 21 ? (25 - i) / 4 : 1; g.globalAlpha = a; g.fillRect(0, y - 90 + i * 20, bw, 20); }
  g.globalAlpha = 1;
  g.fillStyle = 'rgba(236,231,222,.92)'; g.font = `500 30px ${UI}`; g.textAlign = 'left'; g.textBaseline = 'alphabetic';
  g.fillText(r.idx, x, y); g.fillStyle = ACC; g.fillRect(x, y + 18, 40, 4);
  const p = easeOut((t - r.roll[0]) / (r.roll[1] - r.roll[0]));
  const v = r.fig * p, shown = r.dec ? v.toFixed(r.dec) : fmt(Math.round(v));
  g.fillStyle = '#f4efe6'; g.font = `200 150px ${DISPLAY}`;
  const pre = r.approx ? '≈' : '';
  let fx = x - 6;
  if (pre) { g.font = `200 96px ${DISPLAY}`; g.fillText(pre, fx, y + 168); fx += g.measureText(pre).width + 6; g.font = `200 150px ${DISPLAY}`; }
  g.fillText(shown, fx, y + 172);
  const fw = g.measureText(shown).width;
  g.font = `500 40px ${UI}`; g.fillText(r.unit, fx + fw + 12, y + 168);
  g.fillStyle = 'rgba(244,239,230,.95)'; g.font = `500 34px ${UI}`; g.fillText(r.label, x, y + 232);
  let yy = y + 290;
  if (r.legend) {
    const lg = g.createLinearGradient(x, 0, x + 360, 0); lg.addColorStop(0, '#2a1508'); lg.addColorStop(.6, ACC); lg.addColorStop(1, HOT);
    g.fillStyle = lg; g.fillRect(x, y + 262, 360, 10);
    g.fillStyle = 'rgba(236,231,222,.75)'; g.font = `400 24px ${UI}`;
    g.fillText('弱', x, y + 304); g.textAlign = 'right'; g.fillText('信号强', x + 360, y + 304); g.textAlign = 'left';
    yy = y + 352;
  }
  g.fillStyle = 'rgba(236,231,222,.78)'; g.font = `400 26px ${UI}`;
  r.src.forEach((s, i) => g.fillText(s, x, yy + i * 38));
  g.restore();
  if (k > .99) { reg(r.id + 'f', `${pre}${r.fig} ${r.unit}`, x, y + 40, x + 500, y + 180); reg(r.id + 'l', r.label, x, y + 200, x + 600, y + 240); r.src.forEach((s, i) => reg(r.id + 's' + i, s, x, yy - 26 + i * 38, x + 600, yy + 6 + i * 38)); }
}

const PINS = [
  { id: 'p1', t0: T.pin, t1: T.readout2 - .4, anchor: () => S3(.03, -.002, hm), lines: [`这一栋 · ${ST.pick.floors} 层`, `长 ${Math.round(ST.pick.length_m)} 米 · 每 6.5 米一户`] },
  { id: 'p2', lift: 120, t0: T.n1, t1: T.spread + 1.0, anchor: () => { const a = cN1; return [a[0], roofTop(N1), a[1]]; }, lines: [`隔壁 · ${M.b[N1][1]} 层`, `约 ${M.b[N1][2]} 户`] },
  { id: 'p3', lift: 250, t0: T.n2, t1: T.spread + 1.0, anchor: () => { const a = cN2; return [a[0], roofTop(N2), a[1]]; }, lines: [`再隔壁 · ${M.b[N2][1]} 层`, `约 ${M.b[N2][2]} 户`] },
];
function drawPin(p, t) {
  if (t < p.t0 || t > p.t1 + .3) return;
  const grow = easeOut((t - p.t0) / .45) * (1 - easeIn((t - p.t1) / .3));
  const a = proj(...p.anchor()); if (!a || grow <= 0) return;
  const len = (p.lift || 190) * grow, tx = a[0] + 40, ty = a[1] - len;
  g.strokeStyle = 'rgba(244,239,230,.92)'; g.lineWidth = 2; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(tx, ty); g.stroke();
  g.fillStyle = '#f4efe6'; g.beginPath(); g.arc(a[0], a[1], 5, 0, 7); g.fill();
  const k = clamp((grow - .55) / .45); if (k <= 0) return;
  g.font = `500 34px ${UI}`; const w1 = g.measureText(p.lines[0]).width; g.font = `400 26px ${UI}`; const w2 = g.measureText(p.lines[1]).width;
  const bw = Math.max(w1, w2) + 40, by = ty - 104;
  let bx = clamp(tx - 30, 40, W - 40 - bw);
  if (R.some(r => wipe(t, r.t0, r.t1) > 0) && bx < 700 && by < 780) bx = Math.min(W - 40 - bw, 700);
  g.save(); g.beginPath(); g.rect(bx, by, bw * easeOut(k), 104); g.clip();
  plate(bx, by, bw, 104);
  g.fillStyle = '#f4efe6'; g.font = `500 34px ${UI}`; g.fillText(p.lines[0], bx + 20, by + 46);
  g.fillStyle = 'rgba(244,239,230,.82)'; g.font = `400 26px ${UI}`; g.fillText(p.lines[1], bx + 20, by + 86);
  g.restore();
  if (k >= 1) { reg(p.id + 'a', p.lines[0], bx, by, bx + bw, by + 52); reg(p.id + 'b', p.lines[1], bx, by + 52, bx + bw, by + 104); }
}

function drawSub(t) {
  const cue = CUES.find(q => t >= q.t0 && t < q.t1); if (!cue) return;
  const y = 1468;
  const gr = g.createLinearGradient(0, y - 90, 0, y + 70); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(.5, 'rgba(0,0,0,.42)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr; g.fillRect(0, y - 90, W, 160);
  g.fillStyle = '#f7f2e8'; g.font = `500 52px ${UI}`; g.textAlign = 'center'; g.fillText(cue.text, W / 2, y + 18); g.textAlign = 'left';
  const w = g.measureText(cue.text).width; reg('sub', cue.text, W / 2 - w / 2, y - 34, W / 2 + w / 2, y + 30);
}

function drawCard(t) {
  const k = wipe(t, T.card, 99, .7); if (k <= 0) return;
  const x = 64, y = 330;
  g.save(); g.beginPath(); g.rect(0, y - 80, (W - 64) * k, 520); g.clip();
  g.fillStyle = 'rgba(236,231,222,.85)'; g.font = `500 30px ${UI}`; g.fillText('如果……会怎样 · 01', x, y);
  g.fillStyle = '#f7f2e8'; g.font = `500 72px ${UI}`; g.fillText('如果眼睛能看见 Wi-Fi', x, y + 104);
  g.fillStyle = ACC; g.fillRect(x, y + 140, 64, 5);
  g.fillStyle = 'rgba(236,231,222,.8)'; g.font = `400 28px ${UI}`;
  g.fillText('白模投影 · 高岛平团地 · 1:1000', x, y + 200);
  g.fillText('数据：国土交通省 PLATEAU（CC BY 4.0）', x, y + 244);
  g.fillText('路由器数量为估算，环距为示意', x, y + 288);
  g.restore();
  if (k > .99) { reg('c0', '如果……会怎样 · 01', x, y - 30, x + 400, y + 6); reg('c1', '如果眼睛能看见 Wi-Fi', x, y + 40, x + 820, y + 120); }
}

// ------------------------------------------------------------------ render(t)
window.DUR = TL.dur;
window.render = t => {
  TEXTS.length = 0;
  U.uNow.value = t;
  lightState(t);
  placeCamera(t);
  post.composer.render();
  g.clearRect(0, 0, W, H);
  if (QS.has('clean')) return;            // the picture alone (covers)
  for (const r of R) drawReadout(r, t);
  for (const p of PINS) drawPin(p, t);
  drawCard(t);
  drawSub(t);
};
window.seek = window.render;
window.TEXTS = t => { window.render(t); return TEXTS.slice(); };
await document.fonts.load(`200 150px ${DISPLAY}`); await document.fonts.load(`500 34px ${UI}`); await document.fonts.load(`400 24px ${UI}`);
window.render(0);
window.READY = true;
