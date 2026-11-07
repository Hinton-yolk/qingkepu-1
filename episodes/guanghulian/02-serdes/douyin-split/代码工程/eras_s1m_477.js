// 第 1 条 · 纯动画版 v2（上下对比），配曲 Mixkit #477。时间表 split/s1m_477.json（tools/build_nv2.py）
window.FILM_SIZE = [1080, 1920];
window.SPLIT_PATH = 'split/s1m_477.json';
window.SCENE_LIBS = ['split/core.js', 'split/tech.js', 'split/k1n.js'];
(() => { const x = new XMLHttpRequest(); x.open('GET', window.SPLIT_PATH, false); x.send(); const D = JSON.parse(x.responseText);
  window.ERAS = [{ id: 'split', dur: D.dur }]; })();
