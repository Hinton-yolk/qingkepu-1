// 白话光互连 01 · 旁白完整版（重点字幕）。布局和时间表：full/desk_voice.json（由 ../tools/build_desk_voice.py 生成，配乐读同一份）
//   预览 index.html?film=ep1v   渲染 FILM=ep1v node ../render.mjs …
window.FILM_SIZE = [1080, 1920];
window.PUNCH = 0;
window.DESK_PATH = 'full/desk_voice.json';
window.SHOW_SUBS = true;
window.SCENE_LIBS = ['full/film.js', 'full/cards.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', window.DESK_PATH, false); x.send(); const D = JSON.parse(x.responseText);
  window.EXTRA_ASSETS = Object.values(D.clips).map(c => c.src); window.ERAS = [{ id: 'full', dur: D.dur }]; })();
