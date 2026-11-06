// 白话光互连 04《检修站：模糊的信号怎么修回来？》Vox 竖屏。布局和时间表：ep4/desk.json（由 ../tools/build_desk.py 生成，配乐读同一份）
//   预览 index.html?film=ep4   渲染 FILM=ep4 FPS=60 node ../render.mjs 0 <dur> 4 frames
window.FILM_SIZE = [1080, 1920];
window.PUNCH = 0;
window.SCENE_LIBS = ['ep4/film.js', 'ep4/cards_base.js', 'ep4/cards_ep4.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', 'ep4/desk.json', false); x.send(); const D = JSON.parse(x.responseText);
  window.EXTRA_ASSETS = [...Object.values(D.clips).map(c => c.src), ...Object.values(D.prints || {}).map(p => p.src)]; window.ERAS = [{ id: 'ep4', dur: D.dur }]; })();
