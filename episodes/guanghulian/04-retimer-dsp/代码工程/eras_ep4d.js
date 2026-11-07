// 白话光互连 04 · 小红书版 d。布局和时间表：ep4/desk_d.json（tools/assemble04.py + build_desk_d.py）
window.FILM_SIZE = [1080, 1920];
window.PUNCH = 0;
window.DESK_PATH = 'ep4/desk_d.json';
window.SHOW_SUBS = true;
window.SCENE_LIBS = ['ep4/film.js', 'ep4/cards_base.js', 'ep4/cards_ep4.js', 'ep4/cards_x3.js', 'ep4/cards_x4.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', window.DESK_PATH, false); x.send(); const D = JSON.parse(x.responseText);
  window.EXTRA_ASSETS = [...Object.values(D.clips).map(c => c.src), ...Object.values(D.prints || {}).map(p => p.src)]; window.ERAS = [{ id: 'ep4', dur: D.dur }]; })();
