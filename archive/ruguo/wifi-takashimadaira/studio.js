// A white 1:1000 model of 高島平団地 on a dark plinth, a projector above it, the house lights in the room.
// The only data is Wi-Fi, and it is projected light: added to the lit white surface in the shader, scaled by how squarely
// the surface faces the projector, limited to the throw. Never painted into the material.
// Every lit building shows its homes as windows (floor height = measured height ÷ storeys, one bay per home);
// each window is a router calling out. Which buildings are lit, and when, is state in uniforms set by main.js.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { makePost } from '/core/three/post.js';

export const ACC = '#ff6a1a', HOT = '#ffd2a8';          // the film's one accent: orange = Wi-Fi
const lin = h => new THREE.Color(h);

export function makeStudio(W, H, M, Q = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Q.pr ?? 1); renderer.setSize(W, H);
  renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = .95;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap; renderer.shadowMap.autoUpdate = false;
  document.getElementById('stage').appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, W / H, 0.002, 14);
  const post = makePost(renderer, scene, camera, W, H, { ssaa: Q.ssaa ?? 2, ao: false });
  post.bloom.strength = .38; post.bloom.radius = .55; post.bloom.threshold = .82;
  post.vig.uniforms.amt.value = .46;

  { // the room: dark, a faint pool of light behind the plinth
    const c = document.createElement('canvas'); c.width = 288; c.height = 512;
    const g = c.getContext('2d'), gr = g.createRadialGradient(144, 300, 10, 144, 300, 380);
    gr.addColorStop(0, '#1a1c1f'); gr.addColorStop(.55, '#0a0b0c'); gr.addColorStop(1, '#030303');
    g.fillStyle = gr; g.fillRect(0, 0, 288, 512);
    const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; scene.background = tex;
  }
  const pm = new THREE.PMREMGenerator(renderer); scene.environment = pm.fromScene(new RoomEnvironment(), .02).texture;
  scene.environmentIntensity = .1;

  const V2 = THREE.Vector2, V3 = THREE.Vector3;
  const U = {
    uNow: { value: 0 }, uPlate: { value: new V2(M.size[0], M.size[1]) }, uProjPos: { value: new V3(0, 2, .4) },
    uProj: { value: 1 },                                   // projector master (lamp strike, lights up)
    uPick: { value: -1 }, uPickC: { value: new V2() },
    uSeed: { value: new V3() }, uCasc: { value: 0 }, uSeedN: { value: new V2() }, uSeedCell: { value: new V2() }, uHereCell: { value: new V2() },       // the opening: windows catch outward from one seed window (metres)
    uN1: { value: -1 }, uN2: { value: -1 }, uN1T: { value: 1e3 }, uN2T: { value: 1e3 },
    uSpreadT: { value: 1e3 }, uSpreadV: { value: 100 },    // the estate: a building switches on at uSpreadT + distance / uSpreadV
    uRate: { value: 1 },                                   // how fast each window calls (visual, ×2 Hz)
    uSpill: { value: 0 }, uRS: { value: [new V3(), new V3(), new V3()] },   // ring sources: xz + start time
    uRA: { value: new V3() },                              // ring strengths per source
    uHereP: { value: new V3() }, uHereT: { value: 1e3 }, uHereDim: { value: 0 }, uCount: { value: -1 },   // 「我在这儿」: one window calls, one ring leaves it
    uGlow: { value: 0 }, uGlowTex: { value: null },
    cAcc: { value: lin(ACC) }, cHot: { value: lin(HOT) },
  };

  const HEAD = /* glsl */`
  uniform float uCount, uHereDim, uNow, uProj, uPick, uCasc, uN1, uN2, uN1T, uN2T, uSpreadT, uSpreadV, uRate, uSpill, uHereT, uGlow;
  uniform vec2 uPlate, uPickC, uSeedN, uSeedCell, uHereCell; uniform vec3 uProjPos, uSeed, uRA, uHereP, cAcc, cHot; uniform vec3 uRS[3];
  uniform sampler2D uGlowTex;
  varying vec4 vData; varying vec4 vB; varying float vH; varying vec3 vWP; varying vec3 vWN;
  float hash2(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
  float ring(float r, float t0, float lam, float v){       // crests moving outward from t0, only where the wave has arrived
    float age = uNow - t0; if (age <= 0.) return 0.;
    float front = age * v;
    float c = pow(.5 + .5 * cos(6.2831853 * (r - front) / lam), 3.);
    return c * smoothstep(front + 2., front - 10., r);
  }
  // when this building switched on (1e3 = not yet); a short flash follows
  float onTime(){
    float bi = vData.w;
    float t = 1e3;
    if (abs(bi - uPick) < .5) t = -1.;
    if (abs(bi - uN1) < .5) t = min(t, uN1T);
    if (abs(bi - uN2) < .5) t = min(t, uN2T);
    float dB = length(vB.xy - uPickC) * 1000.;
    t = min(t, uSpreadT + dB / uSpreadV + vData.z * .25);
    return t;
  }
  vec3 projLight(float kind){
    vec3 N = normalize(vWN);
    float dirK = .42 + .58 * max(dot(N, normalize(uProjPos - vWP)), 0.);
    vec2 q = abs(vWP.xz) - (uPlate * .5 + .02);
    float thr = 1. - smoothstep(0., .03, max(q.x, q.y));
    if (kind > 1.5) thr *= .25;
    bool bld = kind < .5;
    bool wall = bld && abs(N.y) < .5;
    vec3 c = vec3(0.);
    // the ground glow of the whole estate and the rings that leave the lit slabs
    vec2 uv = vWP.xz / uPlate + .5;
    float G = texture2D(uGlowTex, uv).r;
    c += mix(cAcc, cHot, smoothstep(.75, 1., G)) * G * .55 * uGlow * (wall ? .35 : 1.);
    float rs = 0.;
    for (int i = 0; i < 3; i++) {
      float rm = length(vWP.xz - uRS[i].xy) * 1000.;
      float fo = 1. / (1. + rm / 45.) * smoothstep(240., 40., rm);
      rs += uRA[i] * fo * (.18 + .82 * ring(rm, uRS[i].z, 18., 18.));
    }
    c += cAcc * rs * (wall ? .36 : 1.3) * uSpill;
    { // one ring leaving one window
      float rh = length(vWP - uHereP) * 1000.;
      float age = uNow - uHereT;
      float front = age * 34.;
      float band = exp(-pow((rh - front) / 3.5, 2.)) * step(0., age) * exp(-age * .9);
      c += (cHot * .9 + cAcc * .6) * band * (wall ? .6 : 1.);
    }
    if (bld && vData.y > .5) {
      float tOn = onTime();
      float age = uNow - tOn;
      float lit = step(0., age);
      float isPick = 1. - step(.5, abs(vData.w - uPick));
      if (wall) {
        float floors = vData.y, flH = vH / floors;
        vec2 tg = normalize(vec2(-N.z, N.x));
        float bay = vB.z > 411.5 && vB.z < 414.5 ? .0065 : .0048;
        float along = dot(vWP.xz, tg);
        float fl = floor(vWP.y / flH), cell = floor(along / bay);
        vec2 f = vec2(fract(along / bay), fract(vWP.y / flH));
        float win = smoothstep(.10, .17, f.x) * smoothstep(.90, .83, f.x) * smoothstep(.20, .30, f.y) * smoothstep(.86, .76, f.y);
        float hs = hash2(vec2(cell + vData.w * 37.13, fl));
        float on = step(hs, .93) * lit;
        // the opening: the picked slab's windows catch outward from one window
        vec3 wcen = vec3(vWP.x + tg.x * ((cell + .5) * bay - along), (fl + .5) * flH, vWP.z + tg.y * ((cell + .5) * bay - along));
        float ign = 0., dim = 1., seedW = 0.;
        if (isPick > .5) {
          float face = step(.9, dot(N.xz, uSeedN));
          float isSeed = face * (1. - step(.5, abs(cell - uSeedCell.x))) * (1. - step(.5, abs(fl - uSeedCell.y)));
          float d0 = length(wcen - uSeed) * 1000.;
          seedW = isSeed;
          float d = isSeed > .5 ? 0. : d0 + hs * 14.;
          on = max(isSeed, step(hs, .93)) * step(d, uCasc);
          ign = exp(-max(uCasc - d, 0.) / 7.) * on;
          // 「我在这儿」: one window calls, the rest of the slab holds its breath
          float isHere = face * (1. - step(.5, abs(cell - uHereCell.x))) * (1. - step(.5, abs(fl - uHereCell.y)));
          dim = mix(1. - .7 * uHereDim, 1., isHere);
          float ha = uNow - uHereT;
          ign += isHere * (step(0., ha) * exp(-ha * 2.2) * 2.2 + uHereDim * .8);
          on = max(on, isHere * step(.01, uHereDim));
          // the counter: a band of light reads the slab home by home, bottom to top, landing with the number
          float ord = (fl + clamp(dot(wcen.xz - uPickC, tg) / .1 + .5, 0., 1.)) / floors;
          ign += exp(-pow((ord - uCount) * floors * 1.2, 2.)) * 1.1 * step(0., uCount) * on;
        } else ign = exp(-max(age, 0.) * 7.) * lit * .45;
        float ph = fract(uNow * 2. * uRate + hash2(vec2(hs, fl + cell)));
        if (seedW > .5 && uCasc < 8.) ph = fract(uNow * 2.);   // the first window calls on the beat
        float flash = exp(-ph * 6.);
        c += ((cAcc * (.72 + .55 * flash + 1.2 * ign) + cHot * (.35 * flash + 1.3 * ign)) * win * on + cAcc * .07 * on) * dim;
      } else {
        float roofOn = isPick > .5 ? smoothstep(0., 60., uCasc) : lit;
        c += cAcc * .25 * roofOn + cHot * .35 * exp(-max(age, 0.) * 7.) * lit * (1. - isPick);
      }
    }
    return c * dirK * thr * uProj;
  }`;

  function projMaterial(kind, opts) {
    const m = new THREE.MeshStandardMaterial(opts);
    m.onBeforeCompile = sh => {
      Object.assign(sh.uniforms, U);
      sh.vertexShader = sh.vertexShader
        .replace('#include <common>', `#include <common>\nattribute vec4 aData; attribute vec4 aB; attribute float aH; varying vec4 vData; varying vec4 vB; varying float vH; varying vec3 vWP; varying vec3 vWN;`)
        .replace('#include <fog_vertex>', `#include <fog_vertex>\n vData = aData; vB = aB; vH = aH; vWP = (modelMatrix * vec4(transformed, 1.)).xyz; vWN = normalize(mat3(modelMatrix) * objectNormal);`);
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', `#include <common>\n${HEAD}`)
        .replace('#include <opaque_fragment>', `outgoingLight += projLight(${kind}.0) * mix(diffuseColor.rgb, vec3(1.), .1) * .95;\n#include <opaque_fragment>`);
    };
    m.customProgramCacheKey = () => 'wifiA' + kind;
    return m;
  }

  // ------------------------------------------------------------------ the model: one mesh, outward walls, shared walls skipped
  const hash = n => { const x = Math.sin(n * 91.7 + 17.3) * 43758.5453; return x - Math.floor(x); };
  const ringArea = r => { let a = 0; for (let i = 0; i < r.length; i++) { const [x0, z0] = r[i], [x1, z1] = r[(i + 1) % r.length]; a += x0 * z1 - x1 * z0; } return a / 2; };
  function buildCity() {
    const pos = [], nor = [], dat = [], bb = [], hh = [];
    const put = (p, n, d, b, h) => { pos.push(...p); nor.push(...n); dat.push(...d); bb.push(...b); hh.push(h); };
    const edge = new Map(), k = (a, b, c, d) => `${a},${b},${c},${d}`;
    const cen = new Map();
    for (const [bi, h, rings] of M.p) {
      for (const r of rings) for (let i = 0; i < r.length; i++) {
        const [x0, z0] = r[i], [x1, z1] = r[(i + 1) % r.length]; const kk = k(x0, z0, x1, z1); edge.set(kk, Math.max(edge.get(kk) || 0, h));
      }
      const o = rings[0], s = cen.get(bi) || [0, 0, 0];
      for (const [x, z] of o) { s[0] += x; s[1] += z; s[2]++; }
      cen.set(bi, s);
    }
    for (const [bi, h, rings] of M.p) {
      const [, floors, routers, usage] = M.b[bi];
      const s = cen.get(bi), d = [routers, floors, hash(bi), bi], b = [s[0] / s[2], s[1] / s[2], usage, 0];
      rings.forEach((r, ri) => {
        const sg = (ringArea(r) > 0 ? 1 : -1) * (ri ? -1 : 1);
        for (let i = 0; i < r.length; i++) {
          const [x0, z0] = r[i], [x1, z1] = r[(i + 1) % r.length];
          const dx = x1 - x0, dz = z1 - z0, L = Math.hypot(dx, dz); if (L < 1e-7) continue;
          const nb = edge.get(k(x1, z1, x0, z0)) || 0; if (nb >= h - 1e-6) continue;
          const nx = dz / L * sg, nz = -dx / L * sg;
          const a = [x0, nb, z0], bq = [x1, nb, z1], c = [x1, h, z1], e = [x0, h, z0];
          const cx = (bq[1] - a[1]) * (e[2] - a[2]) - (bq[2] - a[2]) * (e[1] - a[1]);
          const cz = (bq[0] - a[0]) * (e[1] - a[1]) - (bq[1] - a[1]) * (e[0] - a[0]);
          for (const p of (cx * nx + cz * nz > 0 ? [a, bq, c, a, c, e] : [a, c, bq, a, e, c])) put(p, [nx, 0, nz], d, b, h);
        }
      });
      const V = THREE.Vector2, outer = rings[0].map(([x, z]) => new V(x, z)), holes = rings.slice(1).map(r => r.map(([x, z]) => new V(x, z)));
      const all = outer.concat(...holes);
      for (const [i, j, l] of THREE.ShapeUtils.triangulateShape(outer, holes)) {
        const p = all[i], q = all[j], r = all[l];
        const up = (q.y - p.y) * (r.x - p.x) - (q.x - p.x) * (r.y - p.y) > 0;
        for (const v of (up ? [p, q, r] : [p, r, q])) put([v.x, h, v.y], [0, 1, 0], d, b, h);
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
    g.setAttribute('aData', new THREE.Float32BufferAttribute(dat, 4));
    g.setAttribute('aB', new THREE.Float32BufferAttribute(bb, 4));
    g.setAttribute('aH', new THREE.Float32BufferAttribute(hh, 1));
    return g;
  }
  const zero = g => {
    const n = g.attributes.position.count;
    g.setAttribute('aData', new THREE.Float32BufferAttribute(new Float32Array(n * 4).fill(-1), 4));
    g.setAttribute('aB', new THREE.Float32BufferAttribute(new Float32Array(n * 4), 4));
    g.setAttribute('aH', new THREE.Float32BufferAttribute(new Float32Array(n), 1)); return g;
  };

  function build(glowTex) {
    glowTex.colorSpace = THREE.NoColorSpace; glowTex.flipY = false; glowTex.anisotropy = 8; U.uGlowTex.value = glowTex;
    const white = '#f3f3f1';
    const city = new THREE.Mesh(buildCity(), projMaterial(0, { color: white, roughness: .88, metalness: 0 }));
    city.castShadow = city.receiveShadow = true; scene.add(city);
    const PW = M.size[0], PD = M.size[1], RIM = .03, PT = .018;
    const top = new THREE.Mesh(zero(new THREE.PlaneGeometry(PW + RIM * 2, PD + RIM * 2).rotateX(-Math.PI / 2)), projMaterial(1, { color: white, roughness: .9 }));
    top.receiveShadow = true; scene.add(top);
    const box = new THREE.Mesh(zero(new THREE.BoxGeometry(PW + RIM * 2, PT, PD + RIM * 2)), projMaterial(1, { color: '#e9e6e0', roughness: .9 }));
    box.position.y = -PT / 2 - .0004; scene.add(box);
    const plinth = new THREE.Mesh(zero(new THREE.BoxGeometry(PW + .24, .9, PD + .24)), projMaterial(2, { color: '#17181a', roughness: .5 }));
    plinth.position.y = -PT - .45; plinth.receiveShadow = true; scene.add(plinth);
  }

  // house light: a soft key with shadows; dimmed while the data is on, up when the data stops
  const house = new THREE.DirectionalLight('#ffffff', .16);
  house.castShadow = true;
  Object.assign(house.shadow.camera, { left: -.7, right: .7, top: .7, bottom: -.7, near: .2, far: 8 });
  house.shadow.mapSize.set(Q.shadow ?? 4096, Q.shadow ?? 4096); house.shadow.radius = 4; house.shadow.bias = -.0002; house.shadow.normalBias = .0008;
  const hemi = new THREE.HemisphereLight('#dfe7f2', '#141414', .05);
  scene.add(house, house.target, hemi);
  return { renderer, scene, camera, post, U, build, house, hemi };
}
