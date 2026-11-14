// face.js — a small CPU rasteriser for the face (and the mask) with a z-buffer and per-pixel shading.
// The mesh comes from assets/mesh/face.js (MediaPipe's canonical face, Loop-subdivided; cm, y up, z towards the viewer).
// FR.render(opts) draws one view into a canvas region; everything is a pure function of its arguments.
(function (root) {
  "use strict";
  const M = root.FACE;
  const NV = M.v.length / 3, NM = M.mv.length / 3;

  function normals(P, F, n) {                       // area-weighted vertex normals
    const N = new Float32Array(n * 3);
    for (let i = 0; i < F.length; i += 3) {
      const a = F[i] * 3, b = F[i + 1] * 3, c = F[i + 2] * 3;
      const ux = P[b] - P[a], uy = P[b + 1] - P[a + 1], uz = P[b + 2] - P[a + 2];
      const vx = P[c] - P[a], vy = P[c + 1] - P[a + 1], vz = P[c + 2] - P[a + 2];
      const nx = uy * vz - uz * vy, ny = uz * vx - ux * vz, nz = ux * vy - uy * vx;
      for (const k of [a, b, c]) { N[k] += nx; N[k + 1] += ny; N[k + 2] += nz; }
    }
    for (let i = 0; i < n; i++) { const k = i * 3, l = Math.hypot(N[k], N[k + 1], N[k + 2]) || 1; N[k] /= l; N[k + 1] /= l; N[k + 2] /= l; }
    return N;
  }
  const FACE = { P: Float32Array.from(M.v), F: Uint32Array.from(M.f), n: NV,
    A: [M.lips, M.blush, M.shadow, M.contour, M.eyes].map((a) => Float32Array.from(a)) };
  FACE.N = normals(FACE.P, FACE.F, NV);
  const MASK = { P: Float32Array.from(M.mv), F: Uint32Array.from(M.mf), n: NM, A: [Float32Array.from(M.mhem)], clip: true };
  MASK.N = normals(MASK.P, MASK.F, NM);

  // ---- surface points for the dot pattern: seeded, roughly even (one per jittered cell of the front view)
  function mulberry(a) { return function () { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function dotPattern(step = 0.62, seed = 7) {
    const R = mulberry(seed), best = new Map();
    const P = FACE.P, N = FACE.N;
    for (let i = 0; i < NV; i++) {
      if (N[i * 3 + 2] < 0.25) continue;
      const gx = Math.floor((P[i * 3] + 20) / step), gy = Math.floor((P[i * 3 + 1] + 20) / step), k = gx * 1000 + gy;
      const s = R(); const b = best.get(k);
      if (!b || s > b.s) best.set(k, { i, s });
    }
    return [...best.values()].map((b) => b.i).sort((a, b) => a - b);
  }
  const DOTS = dotPattern(1.05, 7);

  // ---- maths
  function rotY(a) { const c = Math.cos(a), s = Math.sin(a); return [c, 0, s, 0, 1, 0, -s, 0, c]; }
  function rotX(a) { const c = Math.cos(a), s = Math.sin(a); return [1, 0, 0, 0, c, -s, 0, s, c]; }
  function mul(A, B) { const C = new Array(9); for (let r = 0; r < 3; r++) for (let c = 0; c < 3; c++) C[r * 3 + c] = A[r * 3] * B[c] + A[r * 3 + 1] * B[3 + c] + A[r * 3 + 2] * B[6 + c]; return C; }
  // the camera: eye, target, fov (deg). Returns a function world → [sx, sy, depth] in the region's pixels.
  function camera(eye, target, fov, w, h, cx = w / 2, cy = h / 2) {
    const f = [target[0] - eye[0], target[1] - eye[1], target[2] - eye[2]], fl = Math.hypot(...f); f[0] /= fl; f[1] /= fl; f[2] /= fl;
    let r = [f[1] * 0 - f[2] * 1, f[2] * 0 - f[0] * 0, f[0] * 1 - f[1] * 0];   // f × up(0,1,0)
    r = [-f[2], 0, f[0]]; const rl = Math.hypot(...r) || 1; r = r.map((v) => v / rl);
    const u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]];
    const k = (h / 2) / Math.tan((fov * Math.PI / 180) / 2);
    return { eye, f, r, u, k, cx, cy,
      p(x, y, z) { const dx = x - eye[0], dy = y - eye[1], dz = z - eye[2]; const zc = dx * f[0] + dy * f[1] + dz * f[2];
        return [cx + k * (dx * r[0] + dy * r[1] + dz * r[2]) / zc, cy - k * (dx * u[0] + dy * u[1] + dz * u[2]) / zc, zc]; } };
  }

  // ---- the rasteriser
  let BUF = null;
  function bufs(w, h) {
    if (!BUF || BUF.w !== w || BUF.h !== h) {
      const n = w * h;
      BUF = { w, h, z: new Float32Array(n), nx: new Float32Array(n), ny: new Float32Array(n), nz: new Float32Array(n), d: new Float32Array(n),
        a: [0, 1, 2, 3, 4].map(() => new Float32Array(n)), id: new Uint8Array(n), wx: new Float32Array(n), wy: new Float32Array(n),
        cv: document.createElement("canvas") };
      BUF.cv.width = w; BUF.cv.height = h; BUF.cx = BUF.cv.getContext("2d"); BUF.img = BUF.cx.createImageData(w, h);
    }
    BUF.z.fill(Infinity); BUF.id.fill(0);
    return BUF;
  }
  // mesh: {P, F, N, A, n}; xf: {R (3×3), t:[x,y,z], s}; cam from camera(); id: 1 face, 2 mask
  function raster(B, mesh, xf, cam, id, scale) {
    const n = mesh.n, P = mesh.P, N = mesh.N, R = xf.R, t = xf.t || [0, 0, 0], s = xf.s || 1;
    const X = new Float32Array(n), Y = new Float32Array(n), Z = new Float32Array(n), WX = new Float32Array(n), WY = new Float32Array(n), WZ = new Float32Array(n);
    const NX = new Float32Array(n), NY = new Float32Array(n), NZ = new Float32Array(n);
    for (let i = 0; i < n; i++) {
      const x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
      const wx = s * (R[0] * x + R[1] * y + R[2] * z) + t[0], wy = s * (R[3] * x + R[4] * y + R[5] * z) + t[1], wz = s * (R[6] * x + R[7] * y + R[8] * z) + t[2];
      const q = cam.p(wx, wy, wz); X[i] = q[0] * scale; Y[i] = q[1] * scale; Z[i] = q[2]; WX[i] = wx; WY[i] = wy; WZ[i] = wz;
      const a = N[i * 3], b = N[i * 3 + 1], c = N[i * 3 + 2];
      NX[i] = R[0] * a + R[1] * b + R[2] * c; NY[i] = R[3] * a + R[4] * b + R[5] * c; NZ[i] = R[6] * a + R[7] * b + R[8] * c;
    }
    const F = mesh.F, w = B.w, h = B.h, A = mesh.A, na = A.length;
    for (let k = 0; k < F.length; k += 3) {
      const i0 = F[k], i1 = F[k + 1], i2 = F[k + 2];
      const x0 = X[i0], y0 = Y[i0], x1 = X[i1], y1 = Y[i1], x2 = X[i2], y2 = Y[i2];
      const area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0);
      if (area >= 0) continue;                                   // back-facing (screen y is down)
      let minx = Math.max(0, Math.floor(Math.min(x0, x1, x2))), maxx = Math.min(w - 1, Math.ceil(Math.max(x0, x1, x2)));
      let miny = Math.max(0, Math.floor(Math.min(y0, y1, y2))), maxy = Math.min(h - 1, Math.ceil(Math.max(y0, y1, y2)));
      if (minx > maxx || miny > maxy) continue;
      const ia = 1 / area;
      for (let py = miny; py <= maxy; py++) {
        const yy = py + 0.5;
        for (let px = minx; px <= maxx; px++) {
          const xx = px + 0.5;
          const b0 = ((x1 - xx) * (y2 - yy) - (x2 - xx) * (y1 - yy)) * ia;
          const b1 = ((x2 - xx) * (y0 - yy) - (x0 - xx) * (y2 - yy)) * ia;
          const b2 = 1 - b0 - b1;
          if (b0 < 0 || b1 < 0 || b2 < 0) continue;
          const z = b0 * Z[i0] + b1 * Z[i1] + b2 * Z[i2], o = py * w + px;
          if (z >= B.z[o]) continue;
          if (mesh.clip && b0 * A[0][i0] + b1 * A[0][i1] + b2 * A[0][i2] < (mesh.cut || 0)) continue;
          B.z[o] = z; B.id[o] = id;
          B.nx[o] = b0 * NX[i0] + b1 * NX[i1] + b2 * NX[i2]; B.ny[o] = b0 * NY[i0] + b1 * NY[i1] + b2 * NY[i2]; B.nz[o] = b0 * NZ[i0] + b1 * NZ[i1] + b2 * NZ[i2];
          B.wx[o] = b0 * WX[i0] + b1 * WX[i1] + b2 * WX[i2]; B.wy[o] = b0 * WY[i0] + b1 * WY[i1] + b2 * WY[i2]; B.d[o] = b0 * WZ[i0] + b1 * WZ[i1] + b2 * WZ[i2];
          for (let j = 0; j < 5; j++) B.a[j][o] = j < na ? b0 * A[j][i0] + b1 * A[j][i1] + b2 * A[j][i2] : 0;
        }
      }
    }
    return { X, Y, Z, WX, WY, WZ };
  }

  const hex = (h) => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  const SKIN = hex("#EBCBA5"), SKIND = hex("#C9996E"), LIP = hex("#C2303A"), BLUSH = hex("#E8907E"), SHADOW = hex("#9A6E6A"), CONT = hex("#9C7354");
  const PLASTER = hex("#ECE9E3"), MASKC = hex("#E3E8EE");
  const clamp = (x, a = 0, b = 1) => (x < a ? a : x > b ? b : x);
  const lerp1 = (a, b, k) => a + (b - a) * k;

  // opts: { ctx, x, y, w, h, scale, cam:{eye,target,fov}, face:{yaw,pitch,t,s}, mode:'skin'|'plaster'|'depth'|'ir',
  //         makeup:{lips,blush,shadow,contour}, mask:0..1 (shown), maskGrey:0..1, eyesOnly:0..1, depthRange:[near,far],
  //         alpha, light:[x,y,z], tint }
  function render(o) {
    const scale = o.scale ?? 0.5, w = Math.ceil(o.w * scale), h = Math.ceil(o.h * scale);
    const B = bufs(w, h);
    const cam = camera(o.cam.eye, o.cam.target, o.cam.fov, o.w, o.h);
    const fo = o.face || {}, R = mul(rotY((fo.yaw || 0) * Math.PI / 180), rotX((fo.pitch || 0) * Math.PI / 180));
    const xf = { R, t: fo.t || [0, 0, 0], s: fo.s || 1 };
    raster(B, FACE, xf, cam, 1, scale);
    if ((o.mask ?? 0) > 0) { MASK.cut = o.maskCut ?? 0; raster(B, MASK, xf, cam, 2, scale); }
    const L = o.light || [-0.45, 0.55, 0.7], ll = Math.hypot(...L), lx = L[0] / ll, ly = L[1] / ll, lz = L[2] / ll;
    const mk = o.makeup || {}, mode = o.mode || "skin", dr = o.depthRange || [-3, 8];
    const img = B.img.data, al = o.alpha ?? 1;
    // camera-facing direction for the 'ir' flood light
    const ex = o.cam.eye;
    for (let p = 0, n = w * h; p < n; p++) {
      const id = B.id[p], q = p * 4;
      if (!id) { img[q + 3] = 0; continue; }
      let nx = B.nx[p], ny = B.ny[p], nz = B.nz[p]; const nl = Math.hypot(nx, ny, nz) || 1; nx /= nl; ny /= nl; nz /= nl;
      const lam = nx * lx + ny * ly + nz * lz, wrap = clamp((lam + 0.35) / 1.35);
      let r, g, b, a = 255 * al;
      const mask = id === 2;
      if (mode === "lines") {
        const st = o.isoStep || 0.6, v = (B.d[p] - (o.isoOff || 0)) / st, fr = v - Math.floor(v), dl = Math.min(fr, 1 - fr) * st;
        const near = clamp((B.d[p] - dr[0]) / (dr[1] - dr[0]));
        const ln = clamp(1 - dl / (o.lineW || 0.07)) * (o.lineK ?? 1) * clamp((B.d[p] - (o.lineMin ?? -99)) * 1.5);
        let eye = 1; if ((o.eyesOnly ?? 0) > 0) eye = 1 - o.eyesOnly * (1 - clamp(B.a[4][p] * 1.4)) * 0.85;
        const gry = mask ? (o.maskGrey ?? 0) : 0;
        const facing = clamp((nz - 0.35) / 0.4);
        const kk = (0.25 + 0.75 * near) * eye * (1 - 0.7 * gry) * facing;
        const c = o.lineCol || [241, 240, 236];
        r = c[0]; g = c[1]; b = c[2];
        a = 255 * al * clamp(ln * kk + (o.fill ?? 0.06) * (0.4 + 0.6 * near) * eye * (0.3 + 0.7 * facing));
      } else if (mode === "depth") {
        const v = clamp((B.d[p] - dr[0]) / (dr[1] - dr[0]));
        let k = 0.08 + 0.92 * Math.pow(v, 1.15);
        k *= 0.82 + 0.18 * wrap;
        const gry = mask ? (o.maskGrey ?? 0) : 0;
        let eye = 1; if ((o.eyesOnly ?? 0) > 0) eye = 1 - o.eyesOnly * (1 - clamp(B.a[4][p] * 1.4)) * 0.6;
        if (mask && gry > 0) k = lerp1(k, 0.3 + 0.12 * wrap, gry);
        r = g = b = 255 * k * eye;
        if (mask && gry > 0) { r *= 0.9; g *= 0.9; b *= 0.95; }
      } else if (mode === "ir") {
        const dx = ex[0] - B.wx[p], dy = ex[1] - B.wy[p], dz = ex[2] - B.d[p], dl = Math.hypot(dx, dy, dz);
        const fl = clamp((nx * dx + ny * dy + nz * dz) / dl);
        let k = 0.18 + 0.72 * Math.pow(fl, 0.9);
        k -= (mk.lips || 0) * B.a[0][p] * 0.07 + (mk.shadow || 0) * B.a[2][p] * 0.05 + (mk.contour || 0) * B.a[3][p] * 0.03;   // makeup: a slight change
        if (mask) k = 0.2 + 0.62 * fl;
        let eye = 1; if ((o.eyesOnly ?? 0) > 0) eye = 1 - o.eyesOnly * (1 - clamp(B.a[4][p] * 1.4)) * 0.82;
        r = g = b = 255 * clamp(k) * eye;
      } else {
        let base = mode === "plaster" ? PLASTER.slice() : SKIN.slice();
        if (mask) base = MASKC.slice();
        else {
          const mixc = (c, k) => { if (k <= 0) return; for (let j = 0; j < 3; j++) base[j] += (c[j] - base[j]) * k; };
          mixc(BLUSH, (mk.blush || 0) * B.a[1][p] * 0.45);
          mixc(SHADOW, (mk.shadow || 0) * B.a[2][p] * 0.55);
          mixc(CONT, (mk.contour || 0) * B.a[3][p] * 0.6);
          mixc(LIP, clamp((mk.lips || 0) * B.a[0][p] * 1.15));
        }
        const sh = 0.55 + 0.45 * wrap;
        const dark = mode === "plaster" ? [118, 116, 112] : (mask ? [150, 158, 168] : SKIND);
        for (let j = 0; j < 3; j++) base[j] = dark[j] + (base[j] - dark[j]) * sh;
        // a soft highlight
        const hx = lx, hy = ly, hz = lz + 1, hl = Math.hypot(hx, hy, hz), sp = Math.pow(clamp((nx * hx + ny * hy + nz * hz) / hl), 40) * (mask ? 0.05 : 0.12 + 0.25 * (mk.lips || 0) * B.a[0][p]);
        r = base[0] + 255 * sp; g = base[1] + 255 * sp; b = base[2] + 255 * sp;
        if ((o.eyesOnly ?? 0) > 0) { const e = 1 - o.eyesOnly * (1 - clamp(B.a[4][p] * 1.4)) * 0.7; r *= e; g *= e; b *= e; }
      }
      if ((o.iso ?? 0) > 0 && !mask) {                       // lines of equal height (every o.isoStep cm), drawn in o.isoCol
        const v = (B.d[p] - (o.isoOff || 0)) / (o.isoStep || 1), fr = v - Math.floor(v), dl = Math.min(fr, 1 - fr) * (o.isoStep || 1);
        const wpx = 0.09, k = o.iso * clamp(1 - dl / wpx) * clamp((B.d[p] - (o.isoMin ?? -99)) * 2);
        if (k > 0) { const c = o.isoCol || [255, 255, 255]; r += (c[0] - r) * k; g += (c[1] - g) * k; b += (c[2] - b) * k; }
      }
      const gn = o.gain ?? 1; img[q] = r * gn; img[q + 1] = g * gn; img[q + 2] = b * gn; img[q + 3] = a;
    }
    B.cx.putImageData(B.img, 0, 0);
    const ctx = o.ctx; ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = "high";
    ctx.drawImage(B.cv, 0, 0, w, h, o.x, o.y, o.w, o.h); ctx.restore();
    return { cam, xf, B, scale };
  }
  // where a face vertex lands on screen for a view (to hang dots, labels and lines on the face)
  function project(o, i, mesh = FACE) {
    const cam = camera(o.cam.eye, o.cam.target, o.cam.fov, o.w, o.h);
    const fo = o.face || {}, R = mul(rotY((fo.yaw || 0) * Math.PI / 180), rotX((fo.pitch || 0) * Math.PI / 180)), t = fo.t || [0, 0, 0], s = fo.s || 1;
    const P = mesh.P, x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
    const wx = s * (R[0] * x + R[1] * y + R[2] * z) + t[0], wy = s * (R[3] * x + R[4] * y + R[5] * z) + t[1], wz = s * (R[6] * x + R[7] * y + R[8] * z) + t[2];
    const q = cam.p(wx, wy, wz); const N = mesh.N;
    const nz = R[6] * N[i * 3] + R[7] * N[i * 3 + 1] + R[8] * N[i * 3 + 2];
    return [o.x + q[0], o.y + q[1], q[2], wx, wy, wz, nz];
  }
  function projectPoint(o, x, y, z) {
    const cam = camera(o.cam.eye, o.cam.target, o.cam.fov, o.w, o.h); const q = cam.p(x, y, z); return [o.x + q[0], o.y + q[1], q[2]];
  }
  // the vertex nearest a canonical point (x, y) on the front of the face
  function nearest(x, y) { let bi = 0, bd = 1e9; const P = FACE.P; for (let i = 0; i < NV; i++) { if (FACE.N[i * 3 + 2] < 0.2) continue; const d = (P[i * 3] - x) ** 2 + (P[i * 3 + 1] - y) ** 2 - 0.01 * P[i * 3 + 2]; if (d < bd) { bd = d; bi = i; } } return bi; }
  // the depth of the face along a vertical line x = x0 (canonical), for the profile line over the nose bridge
  function profile(x0 = 0, y0 = -1, y1 = 4.2, n = 40) {
    const out = []; const P = FACE.P;
    for (let k = 0; k <= n; k++) { const y = y0 + (y1 - y0) * k / n; let best = -1e9; for (let i = 0; i < NV; i++) { if (Math.abs(P[i * 3] - x0) < 0.18 && Math.abs(P[i * 3 + 1] - y) < 0.18) best = Math.max(best, P[i * 3 + 2]); } out.push([y, best]); }
    return out;
  }
  root.FR = { render, project, projectPoint, DOTS, FACE, MASK, nearest, profile, camera };
})(typeof window !== "undefined" ? window : globalThis);
