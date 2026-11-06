"""Timeline for the If-series Wi-Fi episode: places the 15 Fish 「科普」 lines, finds keyword times from the speech check,
and writes film/data.js (window.TL, window.CUES), voice/voice.wav and cues.json. Every visual cue is a word in the narration."""
import json, os, subprocess, io, re
import numpy as np, soundfile as sf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, GRID = 48000, 0.25
L = json.load(open(os.path.join(ROOT, 'voice', 'lines.json')))
WORDS = json.load(open(os.path.join(ROOT, 'voice', 'fish', 'words.json')))
PUN = '，。：；？、！「」 '
GAP = {'L02': .2, 'L03': .75, 'L04': .45, 'L05': .8, 'L06': .5, 'L07': .6, 'L08': .55, 'L09': .45, 'L10': 1.0, 'L11': .55, 'L12': .5, 'L13': .5, 'F1': .6, 'F2': .4, 'E1': .9, 'L15': .9}
SPLIT = {'L06': (['你的身体', '冰箱'], .65)}     # cut a line at its pauses before these words, and open the gap
def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'wav', '-'], capture_output=True, check=True).stdout
    a, _ = sf.read(io.BytesIO(raw)); return a / (np.abs(a).max() + 1e-9) * 0.89
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
    ask=.15, panel=1.0, pak=on('L02') + .15,
    router=k('L03', '路由器亮'), phone=k('L03', '你的手机'),
    neighbor=k('L04', '邻居家'), building=k('L04', '楼上楼下'), glowAll=k('L04', '整栋楼'),
    turn=on('L05'), wobble=k('L05', '没这么整齐'),
    wall=k('L06', '墙会削弱'), body=k('L06', '你的身体'), fridge=k('L06', '冰箱'),
    net=k('L07', '撞在一起'), move=k('L07', '手机挪'),
    street=on('L08') - .3, bt=k('L08', '蓝牙耳机'),
    city=on('L09') - .25, fog=k('L09', '光雾'),
    freeze=on('L10') - .15, cant=k('L10', '根本看不清'),
    prop=on('L11'), ruler=k('L11', '其实一整条波'), long=k('L11', '这么长'),
    pupil=k('L12', '瞳孔'), flash=k('L12', '刚才那些'), blind=k('L12', '一个也看不见'),
    grow=on('L13'), hund=k('L13', '几百米'), q=k('L13', '所以真正的问题'),
    fastIn=on('F1') - .2, fast=k('F1', '中国天眼'), d500=k('F1', '五百米'),
    fear=on('F2'), phones=k('F2', '手机和'), km5=k('F2', '方圆五公里'), ban=k('F2', '禁止带手机'),
    sea=on('E1') - .3, black=end('E1') + .4, next=on('L15'), end=end('L15') + 1.6,
)
C = {k2: round(round(v / GRID) * GRID, 3) for k2, v in C.items()}      # every hit on the half-beat grid (120 BPM)
DUR = round(C['end'], 2)
cues = []
for x in lines:
    t0s = [x['at'](p.replace(' ', '')[:2]) if i else x['t0'] for i, p in enumerate(x['sub'])]
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
