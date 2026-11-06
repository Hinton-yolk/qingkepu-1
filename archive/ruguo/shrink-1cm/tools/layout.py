"""Timeline for If-series 03 (shrink to 1 cm): places the Fish 「科普」 lines, finds keyword times from the speech check,
and writes film/data.js (window.TL, window.CUES), voice/voice.wav and cues.json. Every visual cue is a word in the narration."""
import json, os, subprocess, io, re
import numpy as np, soundfile as sf, pyloudnorm as pyln
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, GRID = 48000, 0.25
L = json.load(open(os.path.join(ROOT, 'voice', 'lines.json')))
WORDS = json.load(open(os.path.join(ROOT, 'voice', 'fish', 'words.json')))
PUN = '，。：；？、！「」“”—— '
GAP = {'L01': .45, 'L03': 1.9, 'L04': .45, 'L05': .45, 'L06': .55, 'L07': .45, 'L08': .45, 'L09': .4, 'L10': .45, 'L11': .45, 'L12': .6, 'L13': .5, 'L14': .5, 'L15': 2.2}
SPLIT = {}
def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'wav', '-'], capture_output=True, check=True).stdout
    a, _ = sf.read(io.BytesIO(raw)); a = a * 10 ** ((-20 - pyln.Meter(SR).integrated_loudness(a)) / 20)      # every line at the same loudness
    return np.tanh(a / .89) * .89 if np.abs(a).max() > .89 else a
def edges(a):
    n = len(a) // 480; db = 20 * np.log10(np.sqrt((a[:n * 480].reshape(n, 480) ** 2).mean(1)) + 1e-9)
    idx = np.where(db > -40)[0]; return idx[0] * .01, (idx[-1] + 1) * .01
norm = lambda s: re.sub(f'[{PUN}]', '', s)
def pauses(a):
    n = len(a) // 480; db = 20 * np.log10(np.sqrt((a[:n * 480].reshape(n, 480) ** 2).mean(1)) + 1e-9)
    out, run, th = [], None, np.percentile(db, 95) - 26
    for i in range(n):
        if db[i] < th: run = i if run is None else run
        else:
            if run is not None and i - run >= 6: out.append(((run + i) / 2) * .01)
            run = None
    return out
voice = np.zeros(int(100 * SR)); lines = []
for l in L:
    a = load(os.path.join(ROOT, 'voice', 'fish', f"{l['id']}.wav")); s0, s1 = edges(a)
    t = .2 if not lines else lines[-1]['t1'] + GAP.get(l['id'], .4)
    on = round(np.ceil(t / GRID) * GRID, 3); start = on - s0
    ch = []
    for w, w0, w1 in WORDS[l['id']]:
        w = norm(w)
        for k in range(len(w)): ch.append(max(s0, w0) + (w1 - w0) * k / max(1, len(w)))
    tts = norm(l['tts'])
    cidx = lambda key, tts=tts, ch=ch: min(len(ch) - 1, round(tts.index(norm(key)) * len(ch) / len(tts)))
    # cuts: (time in the file, extra gap) — the pause just before each split word
    cuts = []
    if l['id'] in SPLIT:
        keys, g = SPLIT[l['id']]; ps = pauses(a)
        for key in keys:
            tk = ch[cidx(key)]; pc = min((p for p in ps if .3 < p < tk + .05), key=lambda p: abs(tk - p), default=tk - .05); cuts.append((pc, g))
    shift = lambda tf, cuts=cuts: sum(g for pc, g in cuts if tf >= pc)
    bounds = [0] + [int(pc * SR) for pc, _ in cuts] + [len(a)]
    for b0, b1 in zip(bounds, bounds[1:]):
        tf = b0 / SR; i0 = int(round((start + tf + shift(tf + 1e-6)) * SR)); voice[i0:i0 + (b1 - b0)] += a[b0:b1]
    def at(key, ch=ch, start=start, cidx=cidx, shift=shift):
        tf = ch[cidx(key)]; return round(start + tf + shift(tf), 3)
    lines.append(dict(id=l['id'], text=l['tts'], t0=round(on, 3), t1=round(start + s1 + shift(s1), 3), at=at, sub=l['sub']))
T = {x['id']: x for x in lines}
k = lambda lid, key: T[lid]['at'](key)
on = lambda lid: T[lid]['t0']; end = lambda lid: T[lid]['t1']
C = dict(
    scene=on('L00'), tea=k('L00', '热茶'),
    ask=on('L01'), cm=k('L01', '一厘米'), what=k('L01', '会发生'),
    pak=end('L01') + .5,
    rice=on('L03'), half=k('L03', '体重'),
    strong=on('L04'), clip=k('L04', '回形针'), lift=k('L04', '一把举'),
    jump=on('L05'), leaf=k('L05', '飘落'), land=k('L05', '毫发无伤'),
    turn=on('L06'),
    rule=on('L07'), surf=k('L07', '表面'),
    drop=on('L08'), wrap=k('L08', '像胶'), heavy=k('L08', '挂着的水'),
    rain=on('L09'), x5=k('L09', '比你重'),
    wind=on('L10'), heat=k('L10', '热量'), minutes=k('L10', '几分钟'),
    food=on('L11'), eat=k('L11', '一天得吃'),
    hero=on('L12'), same=k('L12', '其实'), cause=k('L12', '同一个原因'),
    ant=on('L13'), antp=k('L13', '冷血'), notshrunk=k('L13', '它们不是'),
    back=on('L14'), antgrow=k('L14', '蚂蚁也长不成人'),
    black=end('L14') + 1.9, next=on('L15'), end=end('L15') + 1.6,
)
C = {k2: round(round(v / GRID) * GRID, 3) for k2, v in C.items()}      # every hit on the half-beat grid (120 BPM)
DUR = round(C['end'], 2)
cues = []
for x in lines:
    t0s = [x['at'](re.sub(f'[{PUN}]', '', p)[:2]) if i else x['t0'] for i, p in enumerate(x['sub'])]
    for i, p in enumerate(x['sub']):
        t1 = t0s[i + 1] - .02 if i + 1 < len(t0s) else x['t1'] + .4
        cues.append(dict(t0=round(t0s[i] - .05, 3), t1=round(t1, 3), text=p))
for a, b in zip(cues, cues[1:]): a['t1'] = round(min(a['t1'], b['t0'] - .02), 3)
sf.write(os.path.join(ROOT, 'voice', 'voice.wav'), voice[:int(DUR * SR)].astype(np.float32), SR)
open(os.path.join(ROOT, 'film', 'data.js'), 'w').write('window.TL=' + json.dumps(dict(duration=DUR, lines=[dict(id=x['id'], t0=x['t0'], t1=x['t1']) for x in lines]), ensure_ascii=False)
    + ';\nwindow.CUES=' + json.dumps(dict(c={a: float(b) for a, b in C.items()}, subs=cues), ensure_ascii=False) + ';\n')
json.dump([dict(t0=c['t0'], t1=c['t1'], text=c['text']) for c in cues], open(os.path.join(ROOT, 'cues.json'), 'w'), ensure_ascii=False, indent=1)
for x in lines: print(f"{x['id']} {x['t0']:6.2f}–{x['t1']:6.2f}  {x['text']}")
print('duration', DUR); print({a: round(float(b), 2) for a, b in C.items()})
