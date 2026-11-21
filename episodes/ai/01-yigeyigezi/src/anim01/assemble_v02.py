# V02 成片的帧表：成片时间 → 场景时间（第二、四幕的模型处理压紧），每一帧从「V02 新渲」或「V01 原帧」里取。
# 用法：python3 assemble_v02.py   → out/frames_v02/film/（软链接 + 每帧 JSON，t = 场景时间，ft = 成片时间）+ timemap.json
import os, json, glob
import numpy as np
from scipy.interpolate import PchipInterpolator
H = os.path.dirname(os.path.abspath(__file__))
NEW = os.path.join(H, 'out/frames_v02/v02'); OLD = os.path.join(H, 'out/frames_full/full'); OUT = os.path.join(H, 'out/frames_v02/film')
# (成片时间, 场景时间)：斜率 1 = 原速；第二幕模型处理约 1.4 倍，第四幕「去」进模型约 1.4 倍
KEY = [(0, 0), (4, 4), (8.6, 8.6), (10.2, 10.4), (15.0, 17.0), (16.4, 18.5), (21.0, 23.1), (26.4, 28.5),
       (30.6, 34.4), (32.0, 35.8), (35.7, 39.5), (40.0, 43.8), (68.3, 72.0)]
NEW_RANGES = [(0, 260), (1182, 2160)]          # 场景帧号：这些段用 V02 新渲的帧
def film_to_scene():
    f, s = zip(*KEY); return PchipInterpolator(f, s)
if __name__ == '__main__':
    m = film_to_scene(); FD = KEY[-1][0]; n = int(round(FD * 30))
    os.makedirs(OUT, exist_ok=True)
    for p in glob.glob(os.path.join(OUT, 'f*')): os.remove(p)
    tm = []; src_count = {'new': 0, 'v01': 0}
    for i in range(n):
        st = float(m(i / 30)); si = min(2159, int(round(st * 30)))
        isnew = any(a <= si < b for a, b in NEW_RANGES)
        d = NEW if isnew else OLD; src_count['new' if isnew else 'v01'] += 1
        png = os.path.join(d, f'f{si:05d}.png'); js = json.load(open(png[:-4] + '.json'))
        js['t'] = si / 30; js['ft'] = i / 30; js['f'] = i; js['src'] = ('V02 ' if isnew else 'V01 ') + f'f{si:05d}'
        os.symlink(png, os.path.join(OUT, f'f{i:05d}.png')); json.dump(js, open(os.path.join(OUT, f'f{i:05d}.json'), 'w'), ensure_ascii=False)
        tm.append((i / 30, si / 30))
    json.dump(tm, open(os.path.join(OUT, '..', 'timemap.json'), 'w'))
    print(n, 'frames', src_count)
