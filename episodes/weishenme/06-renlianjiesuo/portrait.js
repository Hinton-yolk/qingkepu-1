// portrait.js — the person, drawn (not modelled): a young woman in profile, facing right (towards the phone).
// Local units: a 1000 × 1000 box (the head about 0..1000 tall); PT.draw(ctx, x, y, s, o) puts the box's origin at (x, y)
// with scale s. o: { makeup: {lips, blush, shadow, contour}, mask: 0..1 (how far it has slid up), grey: 0..1 (an infrared
// look), lipstick: null | {u, away} }. Flat colours, a little soft shading; skin in the series' tone (#EBCBA5 / #D6AD84).
(function (root) {
  "use strict";
  const SKIN = "#EBCBA5", SKIND = "#D6AD84", SKINL = "#F4DEC3", HAIR = "#2A2421", HAIRL = "#3A322D", BROW = "#3B2E27";
  const LIP0 = "#D49A8C", LIP = "#C2303A", BLUSH = "232,144,126", SHADOW = "154,110,106", CONT = "150,105,75";
  const MASKC = "#DDE6EE", MASKD = "#B9C6D2";

  function skinPath() {
    const p = new Path2D();
    p.moveTo(470, 175);
    p.bezierCurveTo(545, 190, 590, 270, 596, 345);
    p.bezierCurveTo(598, 372, 592, 392, 588, 404);
    p.bezierCurveTo(602, 452, 652, 500, 688, 538);
    p.bezierCurveTo(701, 552, 695, 567, 676, 571);
    p.bezierCurveTo(660, 575, 640, 572, 624, 577);
    p.bezierCurveTo(628, 592, 636, 604, 641, 617);
    p.bezierCurveTo(637, 627, 627, 632, 620, 636);
    p.bezierCurveTo(630, 643, 637, 652, 635, 663);
    p.bezierCurveTo(631, 677, 615, 684, 604, 690);
    p.bezierCurveTo(613, 704, 627, 718, 625, 736);
    p.bezierCurveTo(621, 762, 600, 778, 568, 782);
    p.bezierCurveTo(540, 786, 522, 790, 508, 796);
    p.bezierCurveTo(500, 850, 506, 920, 514, 1000);
    p.lineTo(300, 1000);
    p.bezierCurveTo(318, 900, 330, 850, 342, 800);
    p.lineTo(330, 300);
    p.bezierCurveTo(340, 220, 400, 175, 470, 175);
    p.closePath();
    return p;
  }
  function hairPath() {
    const p = new Path2D();
    p.moveTo(470, 176);
    p.bezierCurveTo(540, 168, 600, 210, 612, 282);       // the fringe's front edge, over the top of the forehead
    p.bezierCurveTo(580, 250, 530, 236, 486, 246);
    p.bezierCurveTo(430, 262, 404, 330, 398, 420);       // down in front of the ear's top, then behind it
    p.bezierCurveTo(394, 470, 400, 500, 412, 500);
    p.bezierCurveTo(384, 520, 376, 600, 384, 660);
    p.bezierCurveTo(390, 720, 384, 760, 360, 780);       // the bob's ends
    p.bezierCurveTo(320, 790, 290, 770, 280, 730);
    p.bezierCurveTo(246, 600, 226, 440, 240, 320);
    p.bezierCurveTo(254, 200, 340, 120, 420, 116);
    p.bezierCurveTo(450, 114, 470, 140, 470, 176);
    p.closePath();
    return p;
  }
  function earPath() {
    const p = new Path2D();
    p.moveTo(452, 506);
    p.bezierCurveTo(430, 484, 398, 490, 392, 528);
    p.bezierCurveTo(386, 572, 398, 618, 420, 640);
    p.bezierCurveTo(436, 656, 452, 648, 452, 628);
    p.bezierCurveTo(452, 600, 460, 560, 452, 506);
    p.closePath();
    return p;
  }
  function upperLip() { const p = new Path2D(); p.moveTo(600, 633); p.bezierCurveTo(612, 622, 626, 610, 641, 617); p.bezierCurveTo(637, 627, 627, 632, 620, 636); p.bezierCurveTo(612, 637, 605, 636, 600, 633); p.closePath(); return p; }
  function lowerLip() { const p = new Path2D(); p.moveTo(600, 636); p.bezierCurveTo(608, 638, 614, 637, 620, 636); p.bezierCurveTo(630, 643, 637, 652, 635, 663); p.bezierCurveTo(631, 676, 617, 683, 606, 680); p.bezierCurveTo(602, 664, 600, 650, 600, 636); p.closePath(); return p; }
  function maskPath(k) {                            // the mask in profile: over the nose, the mouth and the chin
    const p = new Path2D();
    p.moveTo(602, 462);
    p.bezierCurveTo(652, 476, 702, 522, 712, 566);
    p.bezierCurveTo(722, 626, 694, 700, 646, 772);
    p.bezierCurveTo(612, 808, 548, 812, 498, 798);
    p.bezierCurveTo(470, 760, 452, 640, 456, 560);
    p.bezierCurveTo(500, 520, 560, 480, 602, 462);
    p.closePath();
    return p;
  }
  const P = { skin: skinPath(), hair: hairPath(), ear: earPath(), ul: upperLip(), ll: lowerLip(), mask: maskPath() };

  function draw(ctx, x, y, s, o = {}) {
    const mk = o.makeup || {}, g = o.grey || 0;
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    if (g > 0) ctx.filter = `grayscale(${g}) contrast(${1 + 0.15 * g}) brightness(${1 + 0.05 * g})`;
    // hair behind (the fringe is drawn again over the skin below)
    ctx.fillStyle = HAIR; ctx.fill(P.hair);
    // skin, with soft shading: darker towards the back of the head and down the neck, a shade under the jaw
    ctx.fillStyle = SKIN; ctx.fill(P.skin);
    ctx.save(); ctx.clip(P.skin);
    let gr = ctx.createLinearGradient(330, 0, 640, 0); gr.addColorStop(0, "rgba(214,173,132,0.75)"); gr.addColorStop(0.45, "rgba(214,173,132,0)"); ctx.fillStyle = gr; ctx.fillRect(250, 100, 500, 950);
    gr = ctx.createLinearGradient(0, 780, 0, 900); gr.addColorStop(0, "rgba(190,140,100,0.55)"); gr.addColorStop(1, "rgba(200,150,108,0.2)"); ctx.fillStyle = gr; ctx.fillRect(290, 790, 240, 220);
    // a light on the forehead, the nose and the cheek
    gr = ctx.createRadialGradient(560, 300, 10, 560, 300, 140); gr.addColorStop(0, "rgba(244,222,195,0.7)"); gr.addColorStop(1, "rgba(244,222,195,0)"); ctx.fillStyle = gr; ctx.fillRect(400, 150, 330, 330);
    gr = ctx.createRadialGradient(640, 500, 4, 640, 500, 60); gr.addColorStop(0, "rgba(250,232,210,0.7)"); gr.addColorStop(1, "rgba(250,232,210,0)"); ctx.fillStyle = gr; ctx.fillRect(560, 420, 160, 160);
    // makeup: blush on the cheek, the contour under the cheekbone, eyeshadow
    if (mk.blush > 0) { gr = ctx.createRadialGradient(540, 520, 5, 540, 520, 70); gr.addColorStop(0, `rgba(${BLUSH},${0.42 * mk.blush})`); gr.addColorStop(1, `rgba(${BLUSH},0)`); ctx.fillStyle = gr; ctx.fillRect(420, 470, 230, 220); }
    if (mk.contour > 0) {
      ctx.save(); ctx.filter = (g > 0 ? ctx.filter + " " : "") + "blur(10px)"; ctx.fillStyle = `rgba(${CONT},${0.38 * mk.contour})`;
      ctx.beginPath(); ctx.moveTo(462, 610); ctx.bezierCurveTo(500, 590, 540, 600, 566, 616); ctx.bezierCurveTo(540, 628, 500, 636, 466, 640); ctx.closePath(); ctx.fill();
      ctx.beginPath(); ctx.moveTo(592, 420); ctx.bezierCurveTo(612, 456, 640, 492, 664, 520); ctx.lineTo(650, 528); ctx.bezierCurveTo(626, 500, 600, 466, 582, 430); ctx.closePath(); ctx.fill();
      ctx.restore();
    }
    if (mk.shadow > 0) { gr = ctx.createRadialGradient(568, 418, 2, 568, 418, 30); gr.addColorStop(0, `rgba(${SHADOW},${0.6 * mk.shadow})`); gr.addColorStop(1, `rgba(${SHADOW},0)`); ctx.fillStyle = gr; ctx.fillRect(530, 380, 80, 70); }
    ctx.restore();
    ctx.strokeStyle = "rgba(201,153,110,0.9)"; ctx.lineWidth = 3; ctx.stroke(P.skin);   // the outline (the hair covers its back)
    ctx.fillStyle = HAIR; ctx.fill(P.hair);
    // the ear (in front of the hair)
    ctx.fillStyle = SKIN; ctx.fill(P.ear); ctx.strokeStyle = SKIND; ctx.lineWidth = 5; ctx.stroke(P.ear);
    ctx.beginPath(); ctx.moveTo(436, 520); ctx.bezierCurveTo(414, 520, 410, 560, 420, 590); ctx.stroke();
    // a strand of hair in front of the ear (the bob's front edge) and the fringe over the forehead
    ctx.strokeStyle = HAIRL; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(330, 170); ctx.bezierCurveTo(280, 300, 272, 520, 300, 720); ctx.stroke();

    // the brow, the eye (open), the lashes
    ctx.strokeStyle = BROW; ctx.lineCap = "round"; ctx.lineWidth = 11; ctx.beginPath(); ctx.moveTo(532, 392); ctx.bezierCurveTo(552, 384, 574, 382, 592, 386); ctx.stroke();
    ctx.fillStyle = "#FBF7F2"; ctx.beginPath(); ctx.moveTo(548, 428); ctx.bezierCurveTo(558, 418, 572, 418, 583, 426); ctx.bezierCurveTo(574, 436, 560, 440, 550, 436); ctx.closePath(); ctx.fill();
    ctx.fillStyle = "#2A211C"; ctx.beginPath(); ctx.ellipse(572, 428, 7, 9, 0, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = "#2A211C"; ctx.lineWidth = 4.5; ctx.beginPath(); ctx.moveTo(546, 427); ctx.bezierCurveTo(558, 416, 574, 416, 586, 425); ctx.stroke();
    ctx.lineWidth = 3; for (let i = 0; i < 4; i++) { const u = 0.45 + i * 0.17, xx = 556 + u * 28, yy = 419 + i * 0.6; ctx.beginPath(); ctx.moveTo(xx, yy); ctx.lineTo(xx + 9, yy - 9 + i); ctx.stroke(); }
    ctx.strokeStyle = "rgba(160,110,80,0.6)"; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(552, 438); ctx.bezierCurveTo(562, 442, 574, 438, 582, 430); ctx.stroke();
    // the nostril, the lips
    ctx.strokeStyle = SKIND; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(648, 562); ctx.bezierCurveTo(640, 552, 628, 554, 626, 566); ctx.stroke();
    const lk = Math.min(1, mk.lips || 0);
    const lipCol = mixC(LIP0, LIP, lk);
    ctx.fillStyle = lipCol; ctx.fill(P.ul); ctx.fill(P.ll);
    ctx.fillStyle = `rgba(255,255,255,${0.12 + 0.2 * lk})`; ctx.beginPath(); ctx.ellipse(622, 650, 7, 4, 0.4, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = "rgba(120,40,40,0.5)"; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(600, 635); ctx.bezierCurveTo(608, 637, 614, 637, 620, 636); ctx.stroke();
    // the mask (slides up from below the chin)
    const mm = o.mask || 0;
    if (mm > 0) {
      ctx.save(); ctx.beginPath(); ctx.rect(300, 900 - mm * 470, 500, 600); ctx.clip();
      ctx.fillStyle = MASKC; ctx.fill(P.mask); ctx.strokeStyle = MASKD; ctx.lineWidth = 4; ctx.stroke(P.mask);
      ctx.strokeStyle = "rgba(150,165,180,0.55)"; ctx.lineWidth = 3;
      for (const yy of [600, 660, 720]) { ctx.beginPath(); ctx.moveTo(470, yy - 20); ctx.bezierCurveTo(560, yy - 10, 640, yy, 700, yy + 10); ctx.stroke(); }
      ctx.strokeStyle = "#C9D3DC"; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(462, 600); ctx.bezierCurveTo(440, 590, 430, 560, 440, 520); ctx.stroke();
      ctx.restore();
    }
    ctx.restore();
  }
  function mixC(a, b, k) { const p = [1, 3, 5].map((i) => parseInt(a.slice(i, i + 2), 16)), q = [1, 3, 5].map((i) => parseInt(b.slice(i, i + 2), 16)); return `rgb(${p.map((v, i) => Math.round(v + (q[i] - v) * k)).join(",")})`; }
  // local points the film hangs things on
  const PTS = { lipL: [600, 650], lipR: [630, 652], nose: [690, 545], eye: [570, 428], bridge: [600, 430], chin: [620, 740] };
  // the profile line down the nose bridge (for the 修容 beat)
  const BRIDGE = [[588, 404], [606, 440], [630, 470], [656, 500], [678, 524], [692, 545]];
  root.PT = { draw, PTS, BRIDGE };
})(typeof window !== "undefined" ? window : globalThis);
