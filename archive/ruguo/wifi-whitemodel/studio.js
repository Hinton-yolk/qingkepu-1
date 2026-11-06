// A white 1:1000 model of a real place on a dark plinth, a projector above it, house lights down.
// The only data is Wi-Fi, and it is projected light: added to the lit white surface in the shader, scaled by how squarely
// the surface faces the projector, limited to the throw. Never painted into the material.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { makePost } from '/core/three/post.js';

export const ACC = '#ff6a1a', HOT = '#ffd2a8';          // the series' one accent: orange = Wi-Fi
const lin = h => new THREE.Color(h);

export function makeStudio(W, H, M, mode, Q = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: false, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Q.pr ?? 2); renderer.setSize(W, H);
  renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = .95;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap; renderer.shadowMap.autoUpdate = false;
  document.getElementById('stage').appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, W / H, 0.004, 12);
  const post = makePost(renderer, scene, camera, W, H, { ssaa: Q.ssaa ?? 2, ao: (Q.ao ?? true) && mode === 0, aoRadius: .02, aoScale: 1.3, aoThickness: .03, aoAmt: .8 });
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

  const U = {
    uMode: { value: mode }, uNow: { value: 0 }, uPlate: { value: new THREE.Vector2(M.size[0], M.size[1]) },
    uProjPos: { value: new THREE.Vector3(0, 2, .4) },
    // A: the picked slab and its homes
    uPickC: { value: new THREE.Vector2() }, uPickAxis: { value: new THREE.Vector2(1, 0) }, uBay: { value: .0065 },
    uFloorH: { value: .003 }, uFill: { value: 0 }, uSpill: { value: 0 }, uPickBase: { value: 0 },
    // B: the whole field as a texture the projector throws
    uWifi: { value: null }, uWifiOn: { value: 0 },
    // C: a level of light rising up every facade
    uLevel: { value: -1 }, uLevelOn: { value: 0 },
    cAcc: { value: lin(ACC) }, cHot: { value: lin(HOT) },
  };

  const HEAD = /* glsl */`
  uniform float uMode, uNow, uBay, uFloorH, uFill, uSpill, uPickBase, uWifiOn, uLevel, uLevelOn;
  uniform vec2 uPlate, uPickC, uPickAxis; uniform vec3 uProjPos, cAcc, cHot; uniform sampler2D uWifi;
  varying vec4 vData; varying float vH; varying vec3 vWP; varying vec3 vWN;
  float hash2(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
  float aaLine(float x, float period, float w){ float d = abs(fract(x / period + .5) - .5) * period; float fw = fwidth(x); return 1. - smoothstep(w, w + fw * 1.5, d); }
  // kind 0 building, 1 plate, 2 plinth
  vec3 projLight(float kind){
    vec3 N = normalize(vWN);
    float dirK = .42 + .58 * max(dot(N, normalize(uProjPos - vWP)), 0.);
    vec2 q = abs(vWP.xz) - (uPlate * .5 + .02);
    float thr = 1. - smoothstep(0., .03, max(q.x, q.y));
    if (kind > 1.5) thr *= .25;
    bool bld = kind < .5;
    bool wall = bld && abs(N.y) < .5;
    vec3 c = vec3(0.);
    if (uMode < .5) {
      // A · one slab: every home is a window of light; its router's signal spills over the estate in rings
      float rm = length(vWP.xz - uPickC) * 1000.;                         // metres from the slab
      float crest = pow(.5 + .5 * cos(6.2831853 * (rm - uNow * 16.) / 18.), 3.);
      float fo = 1. / (1. + rm / 45.) * smoothstep(240., 40., rm);
      c += cAcc * fo * (.18 + .82 * crest) * .55 * (wall ? .45 : 1.) * uSpill;
      if (vData.w > .5) {
        if (wall) {
          float along = dot(vWP.xz, uPickAxis), y = vWP.y - uPickBase;
          float fl = floor(y / uFloorH), cell = floor(along / uBay);
          vec2 f = vec2(fract(along / uBay), fract(y / uFloorH));
          float win = smoothstep(.10, .17, f.x) * smoothstep(.90, .83, f.x) * smoothstep(.20, .30, f.y) * smoothstep(.86, .76, f.y);
          float hs = hash2(vec2(cell, fl));
          float on = step(hs, uFill);
          float beat = fract(uNow * 1.6667 + fract(hs * 7.31));
          float flash = exp(-beat * 7.);
          c += (cAcc * (.75 + .9 * flash) + cHot * .55 * flash) * win * on + cAcc * .07 * on;
        } else c += cAcc * .25 * uFill;
      }
    } else if (uMode < 1.5) {
      // B · the whole neighbourhood: the field lands on roofs and streets; no building, no light
      vec2 uv = vWP.xz / uPlate + .5;
      float F = texture2D(uWifi, vec2(uv.x, uv.y)).r;
      float up = wall ? .4 : 1.;
      c += mix(cAcc, cHot, smoothstep(.82, 1., F)) * F * 1.15 * up * uWifiOn;
    } else {
      // C · a level of light climbs every facade at once: below it the city is soaked
      float s = vWP.y - uLevel;
      float below = smoothstep(.0025, -.0025, s) * uLevelOn;
      if (bld) {
        float flh = vData.y > 0. ? vH / vData.y : .0034;
        float lines = wall ? aaLine(vWP.y, flh, .00022) : 0.;
        c += (cAcc * (.38 + .22 * vData.z) + cHot * .35 * lines) * below;
        c += cHot * exp(-s * s / 2.0e-5) * .55 * uLevelOn * step(-.0005, vH - uLevel + .0005);
      } else c += cAcc * .2 * below;
    }
    return c * dirK * thr;
  }`;

  function projMaterial(kind, opts) {
    const m = new THREE.MeshStandardMaterial(opts);
    m.onBeforeCompile = sh => {
      Object.assign(sh.uniforms, U);
      sh.vertexShader = sh.vertexShader
        .replace('#include <common>', `#include <common>\nattribute vec4 aData; attribute float aH; varying vec4 vData; varying float vH; varying vec3 vWP; varying vec3 vWN;`)
        .replace('#include <fog_vertex>', `#include <fog_vertex>\n vData = aData; vH = aH; vWP = (modelMatrix * vec4(transformed, 1.)).xyz; vWN = normalize(mat3(modelMatrix) * objectNormal);`);
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', `#include <common>\n${HEAD}`)
        .replace('#include <opaque_fragment>', `outgoingLight += projLight(${kind}.0) * mix(diffuseColor.rgb, vec3(1.), .1) * .95;\n#include <opaque_fragment>`);
    };
    m.customProgramCacheKey = () => 'wifi' + kind;
    return m;
  }

  // ------------------------------------------------------------------ the model: one mesh, outward walls, shared walls skipped
  const hash = n => { const x = Math.sin(n * 91.7 + 17.3) * 43758.5453; return x - Math.floor(x); };
  const ringArea = r => { let a = 0; for (let i = 0; i < r.length; i++) { const [x0, z0] = r[i], [x1, z1] = r[(i + 1) % r.length]; a += x0 * z1 - x1 * z0; } return a / 2; };
  function buildCity(pick) {
    const pos = [], nor = [], dat = [], hh = [];
    const put = (p, n, d, h) => { pos.push(...p); nor.push(...n); dat.push(...d); hh.push(h); };
    const edge = new Map(), k = (a, b, c, d) => `${a},${b},${c},${d}`;
    for (const [, h, rings] of M.p) for (const r of rings) for (let i = 0; i < r.length; i++) {
      const [x0, z0] = r[i], [x1, z1] = r[(i + 1) % r.length]; const kk = k(x0, z0, x1, z1); edge.set(kk, Math.max(edge.get(kk) || 0, h));
    }
    for (const [bi, h, rings] of M.p) {
      const [, floors, routers] = M.b[bi];
      const d = [routers, floors, hash(bi), bi === pick ? 1 : 0];
      rings.forEach((r, ri) => {
        const s = (ringArea(r) > 0 ? 1 : -1) * (ri ? -1 : 1);
        for (let i = 0; i < r.length; i++) {
          const [x0, z0] = r[i], [x1, z1] = r[(i + 1) % r.length];
          const dx = x1 - x0, dz = z1 - z0, L = Math.hypot(dx, dz); if (L < 1e-7) continue;
          const nb = edge.get(k(x1, z1, x0, z0)) || 0; if (nb >= h - 1e-6) continue;
          const nx = dz / L * s, nz = -dx / L * s;
          const a = [x0, nb, z0], b = [x1, nb, z1], c = [x1, h, z1], e = [x0, h, z0];
          const cx = (b[1] - a[1]) * (e[2] - a[2]) - (b[2] - a[2]) * (e[1] - a[1]);
          const cz = (b[0] - a[0]) * (e[1] - a[1]) - (b[1] - a[1]) * (e[0] - a[0]);
          for (const p of (cx * nx + cz * nz > 0 ? [a, b, c, a, c, e] : [a, c, b, a, e, c])) put(p, [nx, 0, nz], d, h);
        }
      });
      const V = THREE.Vector2, outer = rings[0].map(([x, z]) => new V(x, z)), holes = rings.slice(1).map(r => r.map(([x, z]) => new V(x, z)));
      const all = outer.concat(...holes);
      for (const [i, j, l] of THREE.ShapeUtils.triangulateShape(outer, holes)) {
        const p = all[i], q = all[j], r = all[l];
        const up = (q.y - p.y) * (r.x - p.x) - (q.x - p.x) * (r.y - p.y) > 0;
        for (const v of (up ? [p, q, r] : [p, r, q])) put([v.x, h, v.y], [0, 1, 0], d, h);
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
    g.setAttribute('aData', new THREE.Float32BufferAttribute(dat, 4));
    g.setAttribute('aH', new THREE.Float32BufferAttribute(hh, 1));
    return g;
  }
  const zero = g => { const n = g.attributes.position.count; g.setAttribute('aData', new THREE.Float32BufferAttribute(new Float32Array(n * 4).fill(-1), 4)); g.setAttribute('aH', new THREE.Float32BufferAttribute(new Float32Array(n), 1)); return g; };

  function build(pick, wifiTex) {
    if (wifiTex) { wifiTex.colorSpace = THREE.NoColorSpace; wifiTex.flipY = false; wifiTex.anisotropy = 8; U.uWifi.value = wifiTex; }
    const white = '#f3f3f1';
    const city = new THREE.Mesh(buildCity(pick), projMaterial(0, { color: white, roughness: .88, metalness: 0 }));
    city.castShadow = city.receiveShadow = true; scene.add(city);
    const PW = M.size[0], PD = M.size[1], RIM = .03, PT = .018;
    const top = new THREE.Mesh(zero(new THREE.PlaneGeometry(PW + RIM * 2, PD + RIM * 2).rotateX(-Math.PI / 2)), projMaterial(1, { color: white, roughness: .9 }));
    top.receiveShadow = true; scene.add(top);
    const box = new THREE.Mesh(zero(new THREE.BoxGeometry(PW + RIM * 2, PT, PD + RIM * 2)), projMaterial(1, { color: '#e9e6e0', roughness: .9 }));
    box.position.y = -PT / 2 - .0004; scene.add(box);
    const plinth = new THREE.Mesh(zero(new THREE.BoxGeometry(PW + .24, .9, PD + .24)), projMaterial(2, { color: '#17181a', roughness: .5 }));
    plinth.position.y = -PT - .45; plinth.receiveShadow = true; scene.add(plinth);
  }

  // house light: down to a dim key (the room is dark; the data is on); a little hemisphere so forms still read
  const house = new THREE.DirectionalLight('#ffffff', .16);
  house.castShadow = true;
  Object.assign(house.shadow.camera, { left: -.7, right: .7, top: .7, bottom: -.7, near: .2, far: 8 });
  house.shadow.mapSize.set(Q.shadow ?? 4096, Q.shadow ?? 4096); house.shadow.radius = 4; house.shadow.bias = -.0002; house.shadow.normalBias = .0008;
  scene.add(house, house.target);
  scene.add(new THREE.HemisphereLight('#dfe7f2', '#141414', .05));
  return { renderer, scene, camera, post, U, build, house };
}
