// 白话光互连 02 · 抖音版（小红书纸桌讲解风格）d。布局和时间表：ep2x/desk_d.json（tools/assemble02.py + build_desk_d.py）
window.FILM_SIZE = [1080, 1920];
window.PUNCH = 0;
window.DESK_PATH = 'ep2x/desk_d.json';
window.SHOW_SUBS = true;
window.SCENE_LIBS = ['ep2x/film.js', 'ep2x/cards_base.js', 'ep2x/cards_ep2.js', 'ep2x/cards_x3.js', 'ep2x/cards_x2.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', window.DESK_PATH, false); x.send(); const D = JSON.parse(x.responseText);
  window.EXTRA_ASSETS = [...Object.values(D.clips).map(c => c.src), ...Object.values(D.prints || {}).map(p => p.src)]; window.ERAS = [{ id: 'ep2x', dur: D.dur }]; })();
