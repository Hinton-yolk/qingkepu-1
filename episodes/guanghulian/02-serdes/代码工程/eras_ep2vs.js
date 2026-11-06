// 白话光互连 02 · 配旁白样片＋旁白字幕。布局和时间表：ep2/desk_voice.json（由 ../tools/build_desk_voice.py 生成）
window.FILM_SIZE = [1080, 1920];
window.PUNCH = 0;
window.DESK_PATH = 'ep2/desk_voice.json';
window.SHOW_SUBS = true;
window.SCENE_LIBS = ['ep2/film.js', 'ep2/cards_base.js', 'ep2/cards_ep2.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', window.DESK_PATH, false); x.send(); const D = JSON.parse(x.responseText);
  window.EXTRA_ASSETS = [...Object.values(D.clips).map(c => c.src), ...Object.values(D.prints || {}).map(p => p.src)]; window.ERAS = [{ id: 'ep2', dur: D.dur }]; })();
