// 白话光互连 01 · 旁白完整版 · B站横屏（1920×1080）。时间表：full/desk_voice_land.json（LAND=1 python3 ../tools/build_desk_voice.py 生成；和竖屏版同一条声音）
//   渲染 FILM=ep1b FW=1920 FH=1080 node ../render.mjs …
window.FILM_SIZE = [1920, 1080];
window.PUNCH = 0;
window.DESK_PATH = 'full/desk_voice_land.json';
window.SHOW_SUBS = true;
window.SCENE_LIBS = ['full/film.js', 'full/cards.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', window.DESK_PATH, false); x.send(); const D = JSON.parse(x.responseText);
  window.EXTRA_ASSETS = Object.values(D.clips).map(c => c.src); window.ERAS = [{ id: 'full', dur: D.dur }]; })();
