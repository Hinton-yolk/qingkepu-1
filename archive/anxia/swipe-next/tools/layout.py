"""Timeline for 「你按下去之后」· 你上划之前: places the Fish 「科普」 lines, finds keyword times from the speech check,
and writes film/data.js (window.TL, window.CUES), voice/voice.wav and cues.json. Every visual cue is a word in the narration."""
import json, os, subprocess, io, re
import numpy as np, soundfile as sf, pyloudnorm as pyln
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, GRID = 48000, 0.25
L = [l for l in json.load(open(os.path.join(ROOT, 'voice', 'lines.json'))) if l['id'] != 'L13']      # no end card: the film ends on 「就是你自己」
WORDS = json.load(open(os.path.join(ROOT, 'voice', 'fish', 'words.json')))
PUN = '，。：；？、！「」“”—— '
GAP = {'L01': .5, 'L02': 1.0, 'L03': .5, 'L04': .45, 'L05': .45, 'L06': .45, 'L07': .45, 'L08': .45, 'L09': .6, 'L10': .6, 'L11': .6, 'L12': .7, 'L13': 2.0}
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
    scene=on('L00'), laugh=k('L00', '笑出声'),
    ask=on('L01'), next1=k('L01', '下一条'), dive=end('L01') + .45,
    dl=on('L02'), queue=k('L02', '后面往往'),
    who=on('L03'),
    you=on('L04'), secs=k('L04', '停留的每一秒'), signal=k('L04', '变成一个信号'), fly=k('L04', '飞回机房'),
    dc=on('L05'), sea=k('L05', '海量'), pick=k('L05', '捞出'),
    q=on('L06'), q1=k('L06', '你会看完'), q2=k('L06', '会点赞'), q3=k('L06', '会评论'), q4=k('L06', '会分享'),
    top=on('L07'), back=k('L07', '送回'),
    swipe=on('L08'), loop=on('L09'),
    rev=on('L10'), rev2=k('L10', '其实'),
    tip=on('L11'), nope=k('L11', '长按'),
    home=on('L12'), self=k('L12', '因为'),
    black=end('L12') + .85, next=end('L12') + .85, end=end('L12') + .85,
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
