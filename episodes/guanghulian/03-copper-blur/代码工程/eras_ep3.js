// 白话光互连 03《电的路：信号为什么越跑越模糊？》Vox 竖屏。布局和时间表：ep3/desk.json（由 ../tools/build_desk.py 生成，配乐读同一份）
//   预览 index.html?film=ep3   渲染 FILM=ep3 FPS=60 node ../render.mjs 0 <dur> 4 frames
window.FILM_SIZE = [1080, 1920];
window.PUNCH = 0;
window.SCENE_LIBS = ['ep3/film.js', 'ep3/cards_base.js', 'ep3/cards_ep3.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', 'ep3/desk.json', false); x.send(); const D = JSON.parse(x.responseText);
  window.EXTRA_ASSETS = [...Object.values(D.clips).map(c => c.src), ...Object.values(D.prints || {}).map(p => p.src)]; window.ERAS = [{ id: 'ep3', dur: D.dur }]; })();
