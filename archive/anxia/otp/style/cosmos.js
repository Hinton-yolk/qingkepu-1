// Style test E: a 3D spectacle, one impossible camera move. three.js + bloom + depth of field; three stills.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
const W = 1080, H = 1920, TAU = Math.PI * 2;
const SERIF = '"Noto Serif CJK SC"', SANS = '"Noto Sans CJK SC"';
function mulberry32(a) { return () => { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
const gl = document.createElement('canvas'); gl.width = W; gl.height = H;
const renderer = new THREE.WebGLRenderer({ canvas: gl, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H, false); renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.1;
const out = document.getElementById('c'); out.width = W; out.height = H; const ctx = out.getContext('2d');

function textTex(draw, w = 1024, h = 512) { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); draw(g, w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; }
function glyph(d, col = '#FF6A3D') { return textTex((g, w, h) => { g.clearRect(0, 0, w, h); g.font = `900 ${h * .86}px ${SERIF}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.shadowColor = col; g.shadowBlur = 30; g.fillStyle = '#FFE2D2'; g.fillText(d, w / 2, h * .54); }, 256, 320); }
function sprite() { return textTex((g, w, h) => { const r = g.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.3, 'rgba(255,255,255,.5)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, w, h); }, 64, 64); }
function dust(n, spread, col, size, seed, center = [0, 0, 0]) {
  const r = mulberry32(seed), pos = new Float32Array(n * 3); for (let i = 0; i < n; i++) { pos[i * 3] = center[0] + (r() - .5) * spread[0]; pos[i * 3 + 1] = center[1] + (r() - .5) * spread[1]; pos[i * 3 + 2] = center[2] + (r() - .5) * spread[2]; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  return new THREE.Points(g, new THREE.PointsMaterial({ color: col, size, map: sprite(), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true }));
}
function smsTex() { return textTex((g, w, h) => {
  const bg = g.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, '#0E1730'); bg.addColorStop(1, '#05070F'); g.fillStyle = bg; g.fillRect(0, 0, w, h);
  g.fillStyle = 'rgba(255,255,255,.92)'; g.font = `700 120px ${SANS}`; g.textAlign = 'center'; g.fillText('21:36', w / 2, 300);
  g.fillStyle = 'rgba(255,255,255,.14)'; g.beginPath(); g.roundRect(40, 520, w - 80, 420, 40); g.fill();
  g.fillStyle = '#FF6A3D'; g.beginPath(); g.roundRect(80, 560, 70, 70, 16); g.fill();
  g.textAlign = 'left'; g.font = `700 40px ${SANS}`; g.fillStyle = 'rgba(255,255,255,.85)'; g.fillText('短信 · 现在', 175, 610);
  g.font = `500 38px ${SANS}`; g.fillStyle = 'rgba(255,255,255,.7)'; g.fillText('【XX银行】您正在进行转账操作，验证码：', 80, 700);
  g.font = `900 110px ${SERIF}`; g.fillStyle = 'rgba(255,106,61,.25)'; g.fillText('836592', 80, 840);
  g.font = `500 32px ${SANS}`; g.fillStyle = 'rgba(255,255,255,.45)'; g.fillText('5 分钟内有效，切勿告知他人。', 80, 905);
}, 900, 1900); }
function phone(scene) {
  const grp = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(7.4, 15.6, .8), new THREE.MeshStandardMaterial({ color: 0x15161c, metalness: .85, roughness: .32 })); grp.add(body);
  const scr = new THREE.Mesh(new THREE.PlaneGeometry(6.8, 15.0), new THREE.MeshBasicMaterial({ map: smsTex(), toneMapped: false })); scr.position.z = .41; grp.add(scr);
  scene.add(grp); return grp;
}
function finger(scene, pos, rot, blurry = true) {
  const m = new THREE.Mesh(new THREE.CapsuleGeometry(.95, 9, 8, 24), new THREE.MeshStandardMaterial({ color: 0xc98a6c, roughness: .55, metalness: 0 }));
  m.position.set(...pos); m.rotation.set(...rot); scene.add(m); return m;
}
function compose(scene, camera, o) {
  const comp = new EffectComposer(renderer); comp.setSize(W, H);
  comp.addPass(new RenderPass(scene, camera));
  if (o.focus) comp.addPass(new BokehPass(scene, camera, { focus: o.focus, aperture: o.aperture ?? .0012, maxblur: o.maxblur ?? .012 }));
  comp.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), o.bloom ?? 1.2, .6, o.threshold ?? .55));
  comp.addPass(new OutputPass()); return comp;
}
function overlay(lines, y, sz, o = {}) {
  ctx.save(); ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
  lines.forEach((parts, i) => { let x = 80; for (const [s, a] of parts) { ctx.font = `900 ${sz}px ${SERIF}`; ctx.fillStyle = a ? '#FF7A4D' : '#F5F2EC'; ctx.shadowColor = a ? 'rgba(255,106,61,.8)' : 'rgba(0,0,0,.6)'; ctx.shadowBlur = a ? 24 : 12; ctx.fillText(s, x, y + i * sz * 1.25); x += ctx.measureText(s).width; } });
  if (o.kicker) { ctx.shadowBlur = 0; ctx.font = `700 34px ${SANS}`; ctx.fillStyle = 'rgba(245,242,236,.6)'; ctx.fillText(o.kicker, 84, y - sz - 20); }
  ctx.restore();
}
const CODE = [...'836592'];
const FR = [
  () => {      // 1 · macro: the phone in the dark, the six digits lifting off the screen, a fingertip out of focus
    const scene = new THREE.Scene(); scene.background = new THREE.Color(0x03050b); scene.fog = new THREE.FogExp2(0x03050b, .012);
    const cam = new THREE.PerspectiveCamera(32, W / H, .1, 400); cam.position.set(-2, -7, 30); cam.lookAt(0, 1.5, 0);
    const p = phone(scene); p.rotation.set(-.38, .14, .05); p.position.y = -3.5;
    scene.add(new THREE.AmbientLight(0x223355, .6)); const key = new THREE.DirectionalLight(0xffc7a0, 1.4); key.position.set(10, 10, 12); scene.add(key); const rim = new THREE.PointLight(0x4f7dff, 60, 60); rim.position.set(-10, 8, -4); scene.add(rim);
    CODE.forEach((d, i) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 1.9), new THREE.MeshBasicMaterial({ map: glyph(d), transparent: true, toneMapped: false, depthWrite: false })); m.position.set(-4.0 + i * 1.42, 2.6 + Math.sin(i * 1.3) * .45 + i * .12, 3.5 + i * .4); m.rotation.set(-.15, .08, (i - 2.5) * .05); scene.add(m); });
    finger(scene, [6.8, -9, 12], [.75, 0, -.45]);
    scene.add(dust(500, [40, 60, 30], 0xffb090, .25, 3, [0, 0, 0]));
    compose(scene, cam, { focus: 26.5, aperture: .0007, maxblur: .01, bloom: .95, threshold: .62 }).render();
    ctx.drawImage(gl, 0, 0); overlay([[['一个验证码，', 0]], [['凭什么能', 0], ['转走你的钱', 1], ['？', 0]]], 300, 92, { kicker: '你按下去之后 · 验证码' });
  },
  () => {      // 2 · inside: the digits fly down a tunnel of light toward a glowing slip far away: 转账 ¥5,000
    const scene = new THREE.Scene(); scene.background = new THREE.Color(0x020309); scene.fog = new THREE.FogExp2(0x020309, .008);
    const cam = new THREE.PerspectiveCamera(55, W / H, .1, 600); cam.position.set(0, -1.5, 18); cam.lookAt(0, 0, -100);
    const r = mulberry32(7);
    for (let i = 0; i < 70; i++) { const z = -i * 6; const col = i % 9 === 0 ? 0xff6a3d : 0x3d8bff; const ring = new THREE.Mesh(new THREE.TorusGeometry(9 + Math.sin(i * .4) * .6, .04 + (i % 9 === 0 ? .05 : 0), 8, 96), new THREE.MeshBasicMaterial({ color: col, toneMapped: false, transparent: true, opacity: .9 })); ring.position.z = z; scene.add(ring); }
    for (let i = 0; i < 260; i++) { const a = r() * TAU, rr = 7.5 + r() * 1.2, len = 2 + r() * 10; const s = new THREE.Mesh(new THREE.BoxGeometry(.05, .05, len), new THREE.MeshBasicMaterial({ color: r() < .15 ? 0xffa070 : 0x7fb4ff, toneMapped: false })); s.position.set(Math.cos(a) * rr, Math.sin(a) * rr, -r() * 400); scene.add(s); }
    CODE.forEach((d, i) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 2.0), new THREE.MeshBasicMaterial({ map: glyph(d), transparent: true, toneMapped: false, depthWrite: false })); m.position.set(-4.4 + i * 1.75, -2.6 + Math.sin(i) * .3, -6 - i * .5); scene.add(m); });
    const slip = new THREE.Mesh(new THREE.PlaneGeometry(16, 5), new THREE.MeshBasicMaterial({ map: textTex((g, w, h) => { g.fillStyle = 'rgba(255,106,61,.18)'; g.beginPath(); g.roundRect(10, 10, w - 20, h - 20, 40); g.fill(); g.strokeStyle = '#FF7A4D'; g.lineWidth = 10; g.stroke(); g.font = `900 ${h * .5}px ${SERIF}`; g.fillStyle = '#FFE6DA'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('转账 ¥5,000', w / 2, h * .54); }, 1024, 320), transparent: true, toneMapped: false })); slip.position.set(0, 3.2, -62); slip.scale.set(.75, .75, 1); scene.add(slip);
    scene.add(dust(900, [24, 24, 300], 0x9fc4ff, .18, 9, [0, 0, -120]));
    compose(scene, cam, { focus: 24, aperture: .0006, maxblur: .008, bloom: 1.15, threshold: .55 }).render();
    ctx.drawImage(gl, 0, 0); overlay([[['其实，它绑着', 0]], [['一件', 0], ['具体的事', 1], ['。', 0]]], 300, 96);
  },
  () => {      // 3 · the confirm: a fingertip on a huge glowing button, shockwaves, money pouring away
    const scene = new THREE.Scene(); scene.background = new THREE.Color(0x05030a); scene.fog = new THREE.FogExp2(0x05030a, .01);
    const cam = new THREE.PerspectiveCamera(40, W / H, .1, 400); cam.position.set(0, 22, 31); cam.lookAt(0, .5, -2);
    const btn = new THREE.Mesh(new THREE.BoxGeometry(12, 1.4, 6.5), new THREE.MeshStandardMaterial({ color: 0xd8401f, emissive: 0xc8361a, emissiveIntensity: .45, roughness: .45 })); btn.position.y = -1; scene.add(btn);
    const lab = new THREE.Mesh(new THREE.PlaneGeometry(11, 4.1), new THREE.MeshBasicMaterial({ map: textTex((g, w, h) => { g.font = `900 ${h * .62}px ${SERIF}`; g.fillStyle = '#FFF4EC'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('确认转账', w / 2, h * .55); }, 1024, 380), transparent: true, toneMapped: false })); lab.rotation.x = -Math.PI / 2; lab.position.set(0, -.28, 0); scene.add(lab);
    for (let i = 0; i < 4; i++) { const ring = new THREE.Mesh(new THREE.TorusGeometry(9 + i * 4.5, .08, 8, 128), new THREE.MeshBasicMaterial({ color: 0xff8a5a, toneMapped: false, transparent: true, opacity: .8 - i * .17 })); ring.rotation.x = Math.PI / 2; ring.position.y = -1.6; scene.add(ring); }
    finger(scene, [2.4, 4.6, .8], [.5, 0, .45]);
    const cr = mulberry32(21); for (let i = 0; i < 26; i++) { const c = new THREE.Mesh(new THREE.CylinderGeometry(.75, .75, .14, 32), new THREE.MeshStandardMaterial({ color: 0xffc35a, metalness: .9, roughness: .28, emissive: 0x5a3200, emissiveIntensity: .6 })); const u = i / 26; c.position.set(4 + u * 10 + (cr() - .5) * 2.5, 1.5 + u * 9 + (cr() - .5) * 2, -3 - u * 12); c.rotation.set(cr() * 3, cr() * 3, cr() * 3); scene.add(c); }
    scene.add(new THREE.AmbientLight(0x332233, .7)); const key = new THREE.PointLight(0xff9a70, 200, 60); key.position.set(0, 6, 6); scene.add(key);
    scene.add(dust(700, [10, 30, 10], 0xffc46b, .45, 13, [14, 10, -14]));
    compose(scene, cam, { focus: 25, aperture: .0007, maxblur: .01, bloom: .8, threshold: .72 }).render();
    ctx.drawImage(gl, 0, 0); overlay([[['你一念，他一按——', 0]], [['系统当成', 0], ['你本人', 1], ['确认。', 0]]], 300, 88);
  },
];
window.seek = async i => { ctx.clearRect(0, 0, W, H); FR[i | 0](); return true; };
window.ready = Promise.all([`900 96px ${SERIF}`, `700 40px ${SANS}`, `500 38px ${SANS}`].map(f => document.fonts.load(f)));
