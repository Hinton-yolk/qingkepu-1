// 白话光互连 01 · Vox 完整版（竖屏）。布局和时间表：full/desk.json（由 ../tools/build_desk.py 生成，配乐读同一份）
//   预览 index.html?film=full   渲染 FILM=full node ../render.mjs 0 <dur> 4 frames_full
window.FILM_SIZE = [1080, 1920];
window.PUNCH = 0;
window.SCENE_LIBS = ['full/film.js', 'full/cards.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', 'full/desk.json', false); x.send(); const D = JSON.parse(x.responseText);
  window.EXTRA_ASSETS = Object.values(D.clips).map(c => c.src); window.ERAS = [{ id: 'full', dur: D.dur }]; })();
