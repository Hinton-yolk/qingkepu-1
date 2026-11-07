// 光互连 03 · 抖音无旁白版 g2。时间表 split/g2.json（tools/build_g.py）
window.FILM_SIZE = [1080, 1920];
window.SPLIT_PATH = 'split/g2.json';
window.SCENE_LIBS = ['split/core.js', 'split/tech.js', 'split/g1.js', 'split/g2.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', window.SPLIT_PATH, false); x.send(); const D = JSON.parse(x.responseText);
  window.ERAS = [{ id: 'split', dur: D.dur }]; })();
