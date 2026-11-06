// 光互连 02 · 抖音拆解版 第 3 条（全屏机制动画）。时间表：split/s3.json（tools/build_split.py）
window.FILM_SIZE = [1080, 1920];
window.SPLIT_PATH = 'split/s3.json';
window.SCENE_LIBS = ['split/core.js', 'split/s3.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', window.SPLIT_PATH, false); x.send(); const D = JSON.parse(x.responseText);
  window.EXTRA_ASSETS = [...new Set(D.shots.flatMap(s => (s.strips || []).map(k => `assets/strips/${k.id}.png`)))];
  window.ERAS = [{ id: 'split', dur: D.dur }]; })();
