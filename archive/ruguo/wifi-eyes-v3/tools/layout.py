"""v3 timeline: places the 11 Fish 「科普」 lines, finds keyword times from the speech check's word timings, and writes
film/data.js (window.TL, window.CUES) + voice/voice.wav + cues.json (subtitles).
Shots start on line onsets; every visual cue is a keyword in the narration (CUE table below)."""
import json, os, subprocess, io, re
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, GRID = 48000, 0.25
L = json.load(open(os.path.join(ROOT, 'voice', 'lines.json')))
WORDS = json.load(open(os.path.join(ROOT, 'voice', 'fish', 'words.json')))
PUN = '，。：；？、！「」 '
GAP = {'V02': 0.9, 'V05': 0.9, 'V07': 0.9, 'V10': 0.9, 'V11': 0.7, 'V04': 0.55, 'V09': 0.5}   # pause before each line (default 0.35)


def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'wav', '-'], capture_output=True, check=True).stdout
    a, _ = sf.read(io.BytesIO(raw)); return a / (np.abs(a).max() + 1e-9) * 0.89


def edges(a):
    n = len(a) // 480; db = 20 * np.log10(np.sqrt((a[:n * 480].reshape(n, 480) ** 2).mean(1)) + 1e-9)
    idx = np.where(db > -40)[0]; return idx[0] * .01, (idx[-1] + 1) * .01


norm = lambda s: re.sub(f'[{PUN}]', '', s)
voice = np.zeros(int(90 * SR)); lines = []; t = 0.3
for l in L:
    a = load(os.path.join(ROOT, 'voice', 'fish', f"{l['id']}.wav")); s0, s1 = edges(a)
    if lines: t = lines[-1]['off'] + GAP.get(l['id'], 0.35)
    on = round(np.ceil(t / GRID) * GRID, 3); start = on - s0
    i0 = int(round(start * SR)); voice[i0:i0 + len(a)] += a
    # character clock: whisper words (relative to the file start) spread over their characters
    ch = []
    for w, w0, w1 in WORDS[l['id']]:
        w = norm(w)
        for k in range(len(w)): ch.append(max(s0, w0) + (w1 - w0) * k / max(1, len(w)))
    tts = norm(l['tts'])
    def at(key, nth=0, tts=tts, ch=ch, start=start):
        i = -1
        for _ in range(nth + 1): i = tts.index(norm(key), i + 1)
        j = min(len(ch) - 1, round(i * len(ch) / len(tts)))
        return round(start + ch[j], 3)
    lines.append(dict(id=l['id'], text=l['tts'], t0=round(on, 3), t1=round(start + s1, 3), start=round(start, 3), off=round(start + s1, 3), at=at, sub=l['sub']))

T = {x['id']: x for x in lines}
k = lambda lid, key, n=0: T[lid]['at'](key, n)
on = lambda lid: T[lid]['t0']
end = lambda lid: T[lid]['t1']
DUR = round(end('V11') + 3.2, 2)

# ------------------------------------------------------------------ shots and cues (every cue is a word in the narration)
SH = [('H1', 0.0), ('S03', on('V02') - .3), ('P1', on('V03') - .25), ('D1', on('V05') - .3), ('M1', on('V06') - .2),
      ('S06', on('V07') - .3), ('B1', on('V08')), ('S11', k('V08', '要像现在') - .15), ('S12', on('V09') - .1),
      ('S13', k('V09', '去看它') - .1), ('R1', on('V10') - .3), ('E1', on('V11') - .2)]
C = dict(
    flip=0.62, hkWall=k('V01', '墙是透明'), hkYou=k('V01', '你却是黑'),
    squiggle=on('V02') - .3, zoomOut=k('V02', '只是波长'), bracket12=k('V02', '十二厘米'), phoneIn=999, ratio=k('V02', '二十五万倍'),
    light=k('V03', '光子越轻'), mol=k('V03', '感光分子'), push=k('V03', '推一下'), flip2=k('V03', '翻身'), wifiPush=k('V03', '的光子太轻'), noMove=k('V03', '推不动'),
    punch=on('V04'), punch2=k('V04', '是它太轻'),
    dna=k('V05', 'DNA'), bond=k('V05', '化学键'), ion=k('V05', '非电离辐射'), heat=k('V05', '微微发热'),
    mw=on('V06'), band=k('V06', '这个频段'), ovenOn=k('V06', '它一开'), lag=k('V06', '会卡'),
    router=k('V07', '路由器'), door=k('V07', '木门'), metal=k('V07', '金属'), body=k('V07', '满身是水'), shadow=k('V07', '黑影'),
    blur=on('V08'), note=k('V08', '要像现在'), steps=[k('V08', '要像现在') + .35 + .3 * i for i in range(4)], halfkm=k('V08', '五百米'),
    hit=on('V09'), panels=on('V09') + .4, tianyan=k('V09', '天眼'), aperture=k('V09', '天眼') + .5, radio=999,
    ring5=k('V09', '去看它'), km5=k('V09', '交手机'), glare=k('V09', '亮得刺眼'),
    refl=k('V10', '反射'), see=k('V10', '看见你'), wall=k('V10', '隔着墙'), echo=k('V10', '反射回来'), breath=k('V10', '呼吸'),
    endEye=on('V11'), endTurn=k('V11', '但'), endCard=end('V11') + .4, blink=end('V11') + 2.2,
)
# phones around the dish switch off one by one after 「交手机」 (S13 reads CUES.phonesOff)
rng = np.random.default_rng(7)
phones_off = sorted(round(C['km5'] + .15 + x, 3) for x in rng.uniform(0, .9, 16))

# subtitles: one cue per 'sub' part, starting at its first character
cues = []
for x in lines:
    t0s = [x['at'](p.replace(' ', '')[:2]) if i else x['t0'] for i, p in enumerate(x['sub'])]
    for i, p in enumerate(x['sub']):
        t1 = t0s[i + 1] - .02 if i + 1 < len(t0s) else x['t1'] + .35
        cues.append(dict(t0=round(t0s[i] - .05, 3), t1=round(t1, 3), text=p))
for a, b in zip(cues, cues[1:]): a['t1'] = round(min(a['t1'], b['t0'] - .02), 3)

sf.write(os.path.join(ROOT, 'voice', 'voice.wav'), voice[:int(DUR * SR)].astype(np.float32), SR)
TLo = dict(duration=DUR, grid=GRID, voice='Fish Audio · 科普 (83bc284d2a3848c8a37f6d9a9ab11cd8)',
           lines=[dict(id=x['id'], text=x['text'], t0=x['t0'], t1=x['t1'], words=[]) for x in lines])
CU = dict(shots=SH, c=C, subs=cues, phonesOff=phones_off, lit={}, grid=GRID)
open(os.path.join(ROOT, 'film', 'data.js'), 'w').write('window.TL=' + json.dumps(TLo, ensure_ascii=False) + ';\nwindow.CUES=' + json.dumps(CU, ensure_ascii=False) + ';\n')
json.dump([dict(t0=c['t0'], t1=c['t1'], text=c['text']) for c in cues], open(os.path.join(ROOT, 'cues.json'), 'w'), ensure_ascii=False, indent=1)
for x in lines: print(f"{x['id']} {x['t0']:6.2f}–{x['t1']:6.2f}  {x['text']}")
print('shots', [(s, round(t, 2)) for s, t in SH]); print('duration', DUR)
print({k2: v for k2, v in C.items() if not isinstance(v, list)})
