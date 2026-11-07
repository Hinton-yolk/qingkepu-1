# 纯动画版 v2（上下对比）时间表：python3 tools/build_nv2.py <曲子id> … → 代码工程/split/s1m_<id>.json
# 镜头时间先按秒设计（DESIGN），再吸附到这首曲子的实测拍点上；曲子从 off 秒处起播，
# off 的选法：让曲子里能量最大的一次抬升（段落切换）正好落在「两张照片并排对比」那一刻（C.compare）。
import sys, json, numpy as np, librosa
DESIGN = dict(route=2.6, pipes=4.6, fast=9.4, bend=11.8, late=13.0, lateEnd=14.6, compare=15.6, faster=19.6, so=23.0, take=25.5, z2=27.6, dur=31.5)
def analyse(path):
    y, sr = librosa.load(path, sr=22050, mono=True); _, bt = librosa.beat.beat_track(y=y, sr=sr, units='time')
    rms = librosa.feature.rms(y=y, hop_length=1102)[0]; e = lambda a, b: float(np.mean(rms[max(0, int(a * 20)):max(1, int(b * 20))]))
    best = None
    for s in bt:
        if s + DESIGN['dur'] + 1 > len(y) / sr: break
        c = s + DESIGN['compare']; jump = e(c, c + 2) - e(c - 2.5, c); body = e(s, s + DESIGN['dur'])
        score = jump / (body + 1e-6) - 0.004 * s + (0 if body > 0.6 * float(np.percentile(rms, 75)) else -1)
        if best is None or score > best[0]: best = (score, float(s))
    off = best[1]; beats = np.array([b - off for b in bt if b >= off - 1e-3])
    return off, beats, float(np.median(np.diff(beats)))
def build(tid):
    off, beats, B = analyse(f'audio/tracks/{tid}.mp3'); snap = lambda x: round(float(beats[np.argmin(np.abs(beats - x))]), 3)
    C = {k: snap(v) for k, v in DESIGN.items() if k != 'dur'}; dur = round(C['z2'] + 4 * B * 2 if C['z2'] + 8 * B < 33 else C['z2'] + 4 * B, 3)
    def line(i, text, t0, t1, kws={}):
        n = len(text); an = sorted([(text.index(w), t) for w, t in kws.items()] + [(0, t0), (n, t1)]); ch = []
        for j in range(n):
            a = max((p for p in an if p[0] <= j), key=lambda p: p[0]); b = min((p for p in an if p[0] > j), key=lambda p: p[0], default=(n, t1))
            ch.append(round(a[1] + (b[1] - a[1]) * (j - a[0]) / max(1, b[0] - a[0]), 3))
        return dict(id=i, t0=t0, t1=t1, clip=t0, text=text, ch=ch, sub=None, big=None, seg='end', src='')
    lines = [line('r1', 'AI 芯片之间寄快递', C['route'], C['pipes'], {'快递': C['route'] + 0.2}),
             line('z1', '路少，反而不会乱。', C['take'], C['z2'], {'路少': C['take'] + 0.3, '不会乱': C['take'] + 1.0}),
             line('z2', '下一条：排成一队以后，对面怎么知道数到了第几个？', C['z2'], dur - 0.3)]
    TK = lambda text, l, a=None, b=None: dict(text=text, line=l, **{'from': a}, to=b)
    shots = [dict(kind='hook', t0=0), dict(kind='route', t0=C['route'], first='r1', topic=''), dict(kind='pipes', t0=C['pipes']),
             dict(kind='take', t0=C['take'], first='z1', cy=700, type=[TK('一句话带走', 'z1'), TK('路少，', 'z1', '路少', '路少'), TK('反而不会乱。', 'z1', '反而', '不会乱')])]
    for k, s in enumerate(shots): s['paper'] = s['kind'] == 'take'; s['t1'] = shots[k + 1]['t0'] if k + 1 < len(shots) else dur
    caps = [[0.0, C['route'] - 0.1, '同一张照片，为什么一张错位了？', 540, 300],
            [C['pipes'] + 0.6, C['fast'] - 0.1, '慢的时候：两边都行', 540, 1500],
            [C['fast'], C['bend'] - 0.2, '一快——', 540, 1500],
            [C['faster'] + 0.2, C['so'] - 0.1, '越快，路越多越难一样长', 540, 1500],
            [C['so'], C['take'] - 0.05, '所以：最快的连接，只修几条路', 540, 1500]]
    D = dict(name=f's1m_{tid}', dur=dur, lines=lines, shots=shots, hudIn=C['route'] + 1.2, caps=caps, bpm=round(60 / B, 2), novoice=True, cue=C, track=tid, off=round(off, 3))
    json.dump(D, open(f'代码工程/split/s1m_{tid}.json', 'w'), ensure_ascii=False)
    open(f'代码工程/eras_s1m_{tid}.js', 'w').write(f"""// 第 1 条 · 纯动画版 v2（上下对比），配曲 Mixkit #{tid}。时间表 split/s1m_{tid}.json（tools/build_nv2.py）
window.FILM_SIZE = [1080, 1920];
window.SPLIT_PATH = 'split/s1m_{tid}.json';
window.SCENE_LIBS = ['split/core.js', 'split/tech.js', 'split/k1n.js'];
(() => {{ const x = new XMLHttpRequest(); x.open('GET', window.SPLIT_PATH, false); x.send(); const D = JSON.parse(x.responseText);
  window.ERAS = [{{ id: 'split', dur: D.dur }}]; }})();
""")
    print(tid, 'off', round(off, 2), 'beat', round(B, 3), 'dur', dur, C)
for tid in sys.argv[1:]: build(tid)
