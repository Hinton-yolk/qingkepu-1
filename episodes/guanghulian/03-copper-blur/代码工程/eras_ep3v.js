// 白话光互连 03 · 旁白版（重点字幕）。布局和时间表：ep3/desk_voice.json（由 ../tools/build_desk_voice.py 生成，配乐读同一份）
window.FILM_SIZE = [1080, 1920];
window.PUNCH = 0;
window.DESK_PATH = 'ep3/desk_voice.json';
window.SHOW_SUBS = true;
window.SCENE_LIBS = ['ep3/film.js', 'ep3/cards_base.js', 'ep3/cards_ep3.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', window.DESK_PATH, false); x.send(); const D = JSON.parse(x.responseText);
  window.EXTRA_ASSETS = [...Object.values(D.clips).map(c => c.src), ...Object.values(D.prints || {}).map(p => p.src)]; window.ERAS = [{ id: 'ep3', dur: D.dur }]; })();
