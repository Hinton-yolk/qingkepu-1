// 光互连 02 · 抖音拆解版 第 2 条（第三稿：一个知识点，科技感画风）。时间表：split/s2.json（tools/build_split.py）
window.FILM_SIZE = [1080, 1920];
window.SPLIT_PATH = 'split/s2.json';
window.SCENE_LIBS = ['split/core.js', 'split/tech.js', 'split/k2.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', window.SPLIT_PATH, false); x.send(); const D = JSON.parse(x.responseText);
  window.ERAS = [{ id: 'split', dur: D.dur }]; })();
