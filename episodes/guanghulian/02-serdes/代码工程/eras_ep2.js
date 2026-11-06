// 白话光互连 02《第一站 出发：SerDes，为什么要把数据排成一列？》Vox 竖屏。布局和时间表：ep2/desk.json（由 ../tools/build_desk.py 生成，配乐读同一份）
//   预览 index.html?film=ep2   渲染 FILM=ep2 FPS=60 node ../render.mjs 0 <dur> 4 frames
window.FILM_SIZE = [1080, 1920];
window.PUNCH = 0;
window.SCENE_LIBS = ['ep2/film.js', 'ep2/cards_base.js', 'ep2/cards_ep2.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', 'ep2/desk.json', false); x.send(); const D = JSON.parse(x.responseText);
  window.EXTRA_ASSETS = [...Object.values(D.clips).map(c => c.src), ...Object.values(D.prints).map(p => p.src)]; window.ERAS = [{ id: 'ep2', dur: D.dur }]; })();
