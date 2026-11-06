// 《如果眼睛能看见 Wi-Fi》 — Projection on White Model, three directions (?dir=A|B|C).
// render(t) is a pure function of t. Every number on screen comes from data/<dir>/stats.json (tools/prep.py).
import * as THREE from 'three';
import { makeStudio, ACC, HOT } from './studio.js';

const W = 1080, H = 1920;
const QS = new URLSearchParams(location.search);
const DIR = (QS.get('dir') || 'A').toUpperCase();
const MODE = { A: 0, B: 1, C: 2 }[DIR];
window.DUR = 6;
const json = u => fetch(u).then(r => { if (!r.ok) throw new Error(u); return r.json(); });
const [M, ST] = await Promise.all([json(`data/${DIR}/model.json`), json(`data/${DIR}/stats.json`)]);

const DRAFT = QS.has('draft');
const S = makeStudio(W, H, M, MODE, DRAFT ? { pr: 1, ssaa: 1, ao: false, shadow: 2048 } : { pr: +(QS.get('pr') || 2), ssaa: +(QS.get('ssaa') || 2), ao: !QS.has('noao'), shadow: 4096 });
const { U, camera, post, renderer, house, scene } = S;
const wifiTex = MODE === 1 ? await new THREE.TextureLoader().loadAsync(`data/${DIR}/wifi.png`) : null;
const PICK = ST.pick.i;
S.build(MODE === 0 ? PICK : -1, wifiTex);

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ss = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const lerp = (a, b, k) => a + (b - a) * k;
const fmt = n => n.toLocaleString('en-US');

// ------------------------------------------------------------------ geometry helpers
const partsOf = bi => M.p.filter(p => p[0] === bi);
function axisOf(bi) {        // long axis of a footprint (PCA)
  const pts = partsOf(bi)[0][2][0]; const n = pts.length;
  const cx = pts.reduce((s, p) => s + p[0], 0) / n, cz = pts.reduce((s, p) => s + p[1], 0) / n;
  let sxx = 0, szz = 0, sxz = 0; for (const [x, z] of pts) { sxx += (x - cx) ** 2; szz += (z - cz) ** 2; sxz += (x - cx) * (z - cz); }
  const a = .5 * Math.atan2(2 * sxz, sxx - szz);
  return { c: [cx, cz], u: [Math.cos(a), Math.sin(a)] };
}
const proj = (x, y, z) => { const v = new THREE.Vector3(x, y, z).project(camera); return v.z < 1 ? [(v.x * .5 + .5) * W, (-v.y * .5 + .5) * H] : null; };

// ------------------------------------------------------------------ per-direction set-up: camera, projector, layer
let P = {};
if (MODE === 0) {
  const { c, u } = axisOf(PICK);
  const hm = ST.pick.h / 1000, fl = ST.pick.floors;
  const n = [-u[1], u[0]];
  U.uPickC.value.set(c[0], c[1]); U.uPickAxis.value.set(u[0], u[1]);
  U.uFloorH.value = hm / fl; U.uBay.value = 6.5 / 1000; U.uPickBase.value = 0;
  // find a viewpoint with a clear line to the slab's facade: test a ring of candidates against every building's box
  const boxes = M.p.filter(p => p[0] !== PICK).map(([, h, rings]) => { const xs = rings[0].map(p => p[0]), zs = rings[0].map(p => p[1]); return [Math.min(...xs), Math.max(...xs), h, Math.min(...zs), Math.max(...zs)]; });
  const hit = (a, b) => boxes.some(([x0, x1, h, z0, z1]) => {       // segment a->b against an axis-aligned box (slab test)
    let t0 = 0, t1 = 1; const d = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], lo = [x0, 0, z0], hi = [x1, h, z1];
    for (let k = 0; k < 3; k++) {
      if (Math.abs(d[k]) < 1e-9) { if (a[k] < lo[k] || a[k] > hi[k]) return false; continue; }
      let ta = (lo[k] - a[k]) / d[k], tb = (hi[k] - a[k]) / d[k]; if (ta > tb) [ta, tb] = [tb, ta];
      t0 = Math.max(t0, ta); t1 = Math.min(t1, tb); if (t0 > t1) return false;
    }
    return true;
  });
  // a crane view: steep enough to look over the neighbouring slabs (same height, ~50 m apart) at the whole facade
  let side = 1, best = null;
  search: for (const sd of [1, -1]) for (const el of [44, 50, 38, 56]) for (const off of [.45, .3, .6, .15]) for (const dist of [.5, .58]) {
    const dir = [n[0] * sd + u[0] * off, n[1] * sd + u[1] * off], L = Math.hypot(...dir), e = el * Math.PI / 180;
    const cam = [c[0] + dir[0] / L * dist * Math.cos(e), dist * Math.sin(e), c[1] + dir[1] / L * dist * Math.cos(e)];
    const facade = [-.04, 0, .04].flatMap(s => [.3, .75].map(k => [c[0] + u[0] * s + n[0] * sd * .006, hm * k, c[1] + u[1] * s + n[1] * sd * .006]));
    if (!facade.some(f => hit(cam, f))) { best = cam; side = sd; break search; }
  }
  P = {
    cam: best || [c[0] + n[0] * .2, .2, c[1] + n[1] * .2],
    tgt: [c[0] + n[0] * side * .012, hm * .8, c[1] + n[1] * side * .012],
    projector: [c[0] + n[0] * .9 * side, 1.1, c[1] + n[1] * .9 * side],
    house: [c[0] - n[0] * 2, 1.4, c[1] - n[1] * 2],
    pin: [c[0] + u[0] * .03, hm, c[1] + u[1] * .03],
    fov: 30, focusK: 1.0, aper: 2.4, pinUp: true,
  };
} else if (MODE === 1) {
  const az = THREE.MathUtils.degToRad(205), el = THREE.MathUtils.degToRad(52), d = 1.85;
  const t0 = [.03, .11, .01];
  P = {
    cam: [t0[0] + Math.sin(az) * Math.cos(el) * d, Math.sin(el) * d, t0[2] - Math.cos(az) * Math.cos(el) * d],
    tgt: t0, projector: [0, 2.4, .5], house: [-1.2, 1.6, -1.0],
    pin: [ST.hole.x, 0, ST.hole.z], fov: 30, focusK: 1.0, aper: 1.4,
  };
} else {
  // the skyline: towers over 100 m, seen side-on from low against the dark
  const tall = M.b.map((b, i) => [b[0], i]).filter(([h]) => h > 100).map(([, i]) => axisOf(i).c);
  const cx = tall.reduce((s, c) => s + c[0], 0) / tall.length, cz = tall.reduce((s, c) => s + c[1], 0) / tall.length;
  const az = THREE.MathUtils.degToRad(150), d = 1.3;
  P = {
    cam: [cx + Math.sin(az) * d, .03, cz - Math.cos(az) * d],
    tgt: [cx + .02, .06, cz], projector: [cx + Math.sin(az) * 1.4, 1.7, cz - Math.cos(az) * 1.4], house: [cx - 1.5, 1.2, cz - 1.0],
    pin: null, fov: 30, focusK: 1.0, aper: 1.6, top: ST.tallest.h / 1000,
  };
}
camera.fov = P.fov; camera.updateProjectionMatrix();
camera.position.set(...P.cam); camera.lookAt(...P.tgt);
U.uProjPos.value.set(...P.projector);
house.position.set(...P.house); house.target.position.set(P.tgt[0], 0, P.tgt[2]); house.target.updateMatrixWorld();
renderer.shadowMap.needsUpdate = true;
post.dof.focus = camera.position.distanceTo(new THREE.Vector3(...P.tgt)) * P.focusK;
post.dof.aper = P.aper; post.dof.maxCoc = 14;
if (post.dof.ao) post.dof.aoAmt = MODE === 0 ? .7 : 0;

// ------------------------------------------------------------------ the 2D layer: readout (left third), pins, subtitle
const ov = document.getElementById('ov'), g = ov.getContext('2d');
const DISPLAY = '"Inter Tight"', UI = '"Noto Sans Mono CJK SC"';
const TXT = {
  A: { idx: '01 · 用 Wi-Fi 的眼睛看', fig: fmt(ST.pick.routers), unit: '户', label: `≈ ${fmt(ST.pick.routers)} 台路由器（估算）`,
       src: `高岛平团地 · 东京板桥区 · 1:1000`, pin: [`这一栋 · ${ST.pick.floors} 层`, `每 6.5 米一户，每户一台`], sub: '整栋楼一闪一闪，像万家灯火' },
  B: { idx: '01 · 用 Wi-Fi 的眼睛看', fig: fmt(ST.routers), unit: '台', label: `路由器（估算）· 半径 ${ST.site.r} 米内`,
       src: `高圆寺 · 东京杉并区 · 1:1000 · 环距放大示意`, pin: ['没有楼的地方', '就没有光'], sub: '隔壁、楼上、楼下，全都亮着' },
  C: { idx: '01 · 用 Wi-Fi 的眼睛看', fig: fmt(ST.routers), unit: '台', label: '路由器与无线接入点（估算）',
       src: `西新宿 · 东京新宿区 · 1:1000`, pin: null, sub: '整座城市，都泡在电磁波里' },
}[DIR];

function plate(x, y, w, h) { g.fillStyle = 'rgba(8,9,10,.62)'; g.fillRect(x, y, w, h); }
function drawReadout(k) {
  if (k <= 0) return;
  const x = 64, y = 300;
  const bg = g.createLinearGradient(0, 0, 640, 0); bg.addColorStop(0, 'rgba(5,6,7,.62)'); bg.addColorStop(.7, 'rgba(5,6,7,.35)'); bg.addColorStop(1, 'rgba(5,6,7,0)');
  const vg = g.createLinearGradient(0, y - 90, 0, y + 430); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(.15, 'rgba(0,0,0,1)'); vg.addColorStop(.85, 'rgba(0,0,0,1)'); vg.addColorStop(1, 'rgba(0,0,0,0)');
  g.save(); g.fillStyle = bg; g.globalAlpha = 1; g.beginPath(); g.rect(0, y - 90, 640, 520); g.clip();
  for (let i = 0; i < 26; i++) { const yy = y - 90 + i * 20; const a = i < 4 ? i / 4 : i > 21 ? (25 - i) / 4 : 1; g.globalAlpha = a; g.fillRect(0, yy, 640, 20); }
  g.restore(); g.globalAlpha = 1;
  g.globalAlpha = 1;
  g.fillStyle = 'rgba(236,231,222,.92)'; g.font = `500 30px ${UI}`; g.textBaseline = 'alphabetic'; g.textAlign = 'left';
  g.fillText(TXT.idx, x, y);
  g.fillStyle = ACC; g.fillRect(x, y + 18, 40, 4);
  const shown = Math.round(parseInt(TXT.fig.replace(/,/g, '')) * ss(k));
  g.fillStyle = '#f4efe6'; g.font = `200 150px ${DISPLAY}`;
  g.fillText(fmt(shown), x - 6, y + 172);
  const fw = g.measureText(fmt(shown)).width;
  g.font = `500 40px ${UI}`; g.fillText(TXT.unit, x + fw + 10, y + 168);
  g.fillStyle = 'rgba(244,239,230,.95)'; g.font = `500 34px ${UI}`; g.fillText(TXT.label, x, y + 230);
  // legend: the projector's one hue
  const lg = g.createLinearGradient(x, 0, x + 360, 0); lg.addColorStop(0, '#2a1508'); lg.addColorStop(.6, ACC); lg.addColorStop(1, HOT);
  g.fillStyle = lg; g.fillRect(x, y + 262, 360, 10);
  g.fillStyle = 'rgba(236,231,222,.75)'; g.font = `400 24px ${UI}`;
  g.fillText('弱', x, y + 304); g.textAlign = 'right'; g.fillText('信号强', x + 360, y + 304); g.textAlign = 'left';
  g.fillText(TXT.src, x, y + 352);
  g.fillText('数据：国土交通省 PLATEAU（CC BY 4.0）', x, y + 388);
}
function drawPin(anchor, k) {
  if (!anchor || !TXT.pin || k <= 0) return;
  const a = proj(anchor[0], anchor[1], anchor[2]); if (!a) return;
  const up = !!P.pinUp, right = up || a[0] < W * .55, len = (up ? 200 : 220) * ss(k), tx = a[0] + (right ? 50 : -50), ty = up ? a[1] - len : Math.max(880, a[1] - len);
  g.strokeStyle = 'rgba(244,239,230,.9)'; g.lineWidth = 2; g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(tx, ty); g.stroke();
  g.fillStyle = '#f4efe6'; g.beginPath(); g.arc(a[0], a[1], 5, 0, 7); g.fill();
  if (k < .6) return;
  g.font = `500 34px ${UI}`; const w1 = g.measureText(TXT.pin[0]).width; g.font = `400 26px ${UI}`; const w2 = g.measureText(TXT.pin[1]).width;
  const bw = Math.max(w1, w2) + 40, bx = up ? Math.min(tx - 30, W - 40 - bw) : right ? tx : tx - bw, by = ty - 104;
  plate(bx, by, bw, 104);
  g.fillStyle = '#f4efe6'; g.font = `500 34px ${UI}`; g.fillText(TXT.pin[0], bx + 20, by + 46);
  g.fillStyle = 'rgba(244,239,230,.82)'; g.font = `400 26px ${UI}`; g.fillText(TXT.pin[1], bx + 20, by + 86);
}
function drawLevel(level) {      // C: the reading rides up with the level, pinned to the tallest tower
  const ti = ST.tallest.i, c = axisOf(ti).c;
  const a = proj(c[0], level, c[1]); if (!a) return;
  g.strokeStyle = 'rgba(255,210,168,.9)'; g.lineWidth = 2; g.beginPath(); g.moveTo(a[0] + 24, a[1]); g.lineTo(a[0] + 150, a[1]); g.stroke();
  plate(a[0] + 150, a[1] - 46, 330, 92);
  g.fillStyle = '#f4efe6'; g.font = `200 52px ${DISPLAY}`; g.fillText(`${Math.round(level * 1000)} m`, a[0] + 170, a[1] + 4);
  g.fillStyle = 'rgba(244,239,230,.82)'; g.font = `400 24px ${UI}`; g.fillText('信号淹到的高度', a[0] + 170, a[1] + 36);
}
function drawSub(text) {
  const y = 1468;
  const gr = g.createLinearGradient(0, y - 90, 0, y + 70); gr.addColorStop(0, 'rgba(0,0,0,0)'); gr.addColorStop(.5, 'rgba(0,0,0,.42)'); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr; g.fillRect(0, y - 90, W, 160);
  g.fillStyle = '#f7f2e8'; g.font = `500 54px ${UI}`; g.textAlign = 'center'; g.fillText(text, W / 2, y + 18); g.textAlign = 'left';
}

// ------------------------------------------------------------------ render(t)
window.render = t => {
  U.uNow.value = t;
  if (MODE === 0) { U.uFill.value = ss(t / 3.2) * .93; U.uSpill.value = ss((t - .4) / 1.6); }
  if (MODE === 1) U.uWifiOn.value = ss(t / 1.2);
  if (MODE === 2) { U.uLevelOn.value = 1; U.uLevel.value = lerp(.0, P.top * 1.04, ss(t / 6)); }
  post.composer.render();
  g.clearRect(0, 0, W, H);
  drawReadout(clamp(t / 1.2));
  if (MODE === 2) drawLevel(U.uLevel.value);
  drawPin(P.pin, clamp((t - .8) / .6));
  drawSub(TXT.sub);
};
await document.fonts.load(`200 150px ${DISPLAY}`); await document.fonts.load(`500 34px ${UI}`); await document.fonts.load(`400 24px ${UI}`);
window.render(0);
window.READY = true;
