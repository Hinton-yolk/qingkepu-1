"""One source of truth for picture and sound (v2).
Reads voice/timeline.json (lines + shots) + beats.json, writes film/data.js (window.TL, window.CUES)
and audio/sfx_events.json. Every cue sits on the measured 8th grid (SFX may use 16ths)."""
import json, os
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, 'voice', 'timeline.json')))
BEATS = json.load(open(os.path.join(ROOT, 'beats.json')))
G = BEATS['grid8']
L = {l['id']: l for l in TL['lines']}
SH = TL['shots']
DUR = TL['duration']


def snap(t, mode='near'):
    if mode == 'up':
        return min((g for g in G if g >= t - 1e-6), default=t)
    if mode == 'down':
        return max((g for g in G if g <= t + 1e-6), default=t)
    return min(G, key=lambda g: abs(g - t))


def chars(lid):
    out = []
    for w in L[lid]['words']:
        n = len(w['w'])
        for i, ch in enumerate(w['w']):
            out.append((ch, w['t0'] + (w['t1'] - w['t0']) * i / n))
    return out


def W(lid, sub):
    """time the substring `sub` starts being spoken in line lid"""
    cs = chars(lid)
    s = ''.join(c for c, _ in cs)
    i = s.find(sub.replace(' ', ''))
    if i < 0:
        raise KeyError(f'{lid}: {sub} not in {s}')
    return cs[i][1]


shots = sorted(SH.items(), key=lambda kv: kv[1])
for k, t in shots:
    assert abs(snap(t) - t) < 1e-6, (k, t)

C = {}
C['eyeOpen'] = 0.0
C['pupilPush'] = 4.2
C['front1'] = snap(W('L02', '光') - 0.15)
C['squiggle'] = 8.4
C['zoomOut'] = snap(W('L04', 'Wi-Fi'))
C['bracket12'] = snap(W('L04', '12'), 'up')
C['phoneIn'] = snap(W('L04', '手机') - 0.2)
C['wipe34'] = 15.9
C['lamp'] = snap(W('L05', '灯') - 0.2)
C['beacons'] = snap(W('L06', '每'), 'down')
C['ssid'] = snap(W('L06', '名字') - 0.3)
C['frost'] = snap(W('L07', '毛玻璃'))
C['nbSide'] = snap(W('L08', '隔壁'))
C['nbUp'] = snap(W('L08', '楼上'))
C['nbDown'] = snap(W('L08', '楼下'))
C['cascade'] = snap(W('L08', '整'))
C['wall'] = snap(W('L09', '墙') - 0.15)
C['body'] = snap(W('L09', '人体') - 0.15)
C['metal'] = snap(W('L09', '金属') - 0.15)
C['blur'] = snap(L['L11']['t0'])
C['pullEye'] = snap(W('L11', '小眼睛') - 0.3)
C['haze'] = snap(W('L11', '光晕') - 0.3)
C['note'] = snap(W('L12', '清楚'))
C['steps'] = [round(C['note'] + 0.6 * i, 4) for i in range(4)]   # one step per beat: coin, person, building, valley
C['halfkm'] = snap(W('L12', '半公里'))
C['hit'] = SH['S12']
C['panels'] = snap(L['L13']['t0'])
C['tianyan'] = snap(W('L13', '中国天眼') - 0.3)
C['aperture'] = snap(W('L13', '口径'))
C['radio'] = snap(W('L13', '专门') - 0.15)
C['ring5'] = snap(L['L14']['t0'])
C['km5'] = snap(W('L14', '5公里') - 0.3)
C['phonesOff'] = snap(W('L14', '禁用') - 0.3)
C['tidy'] = SH['S14']
C['messy'] = snap(W('L15', '反射') - 0.15)
C['soak'] = snap(W('L15', '整座城市') - 0.3)
C['endText'] = snap(L['L16']['t0'] - 0.3)
C['blink'] = snap(DUR - 0.9)

# building cascade: unit -> time (16ths of the measured grid)
cols, floors = 3, 8
home = (1, 6)
first = {(0, 6): C['nbSide'], (2, 6): C['nbSide'] + 0.15, (1, 7): C['nbUp'], (1, 5): C['nbDown']}
rest = sorted([(c, f) for c in range(cols) for f in range(floors) if (c, f) != home and (c, f) not in first],
              key=lambda u: (abs(u[0] - home[0]) + abs(u[1] - home[1]), u[1], u[0]))
lit = {f'{c},{f}': round(t, 4) for (c, f), t in first.items()}
for i, (c, f) in enumerate(rest):
    lit[f'{c},{f}'] = round(C['cascade'] + 0.15 * i, 4)
lit[f'{home[0]},{home[1]}'] = 0.0
phones_off = [round(C['phonesOff'] + 0.15 * i, 4) for i in range(7)]

sfx = []
add = lambda t, k, **kw: sfx.append({'t': t, 'k': k, **kw})
add(0.3, 'bell', n=74, g=0.5)
add(C['pupilPush'], 'rise', n=62, d=0.6, g=0.35)
add(C['front1'], 'gliss', d=0.9, g=0.45)
add(C['squiggle'], 'tick', g=0.2)
add(C['bracket12'], 'pop', n=69, g=0.4)
add(C['phoneIn'], 'pop', n=74, g=0.35)
add(C['wipe34'], 'gliss', d=0.6, g=0.3)
add(C['lamp'], 'tick', g=0.18)
t = C['beacons']
while t < SH['S05'] - 1e-6:
    add(round(t, 4), 'blip', n=86, g=0.22); t += 0.6
for key, n in [('nbSide', 69), ('nbUp', 72), ('nbDown', 74)]:
    add(C[key], 'pop', n=n, g=0.35)
scale = [62, 64, 65, 67, 69, 70, 72, 74, 76, 77, 79, 81, 82, 84]
for i, tt in enumerate(sorted(v for v in lit.values() if v >= C['cascade'])):
    add(tt, 'pluck', n=scale[i % len(scale)] + (12 if i >= len(scale) else 0), g=0.16)
add(SH['S06'] - 0.3, 'rise', n=62, d=0.3, g=0.2)
add(C['wall'], 'pop', n=62, g=0.32)
add(C['body'], 'pop', n=65, g=0.32)
add(C['metal'], 'ting', n=88, g=0.35)
for i, st in enumerate(C['steps']):
    add(st, 'pop', n=[74, 69, 65, 62][i], g=0.3)
add(C['halfkm'], 'pop', n=62, g=0.4)
add(C['panels'], 'bell', n=86, g=0.12)
add(C['tianyan'], 'bell', n=81, g=0.16)
add(C['aperture'], 'tick', g=0.18)
add(C['radio'], 'tick', g=0.18)
add(C['ring5'], 'rise', n=50, d=1.2, g=0.3)
add(C['km5'], 'tick', g=0.2)
for i, tt in enumerate(phones_off):
    add(tt, 'off', n=86 - i, g=0.14)
add(C['messy'], 'bell', n=86, g=0.15)
add(C['soak'], 'rise', n=62, d=1.5, g=0.25)
add(C['endText'], 'tick', g=0.15)
for e in sfx:
    q = round(e['t'] / 0.15) * 0.15
    assert abs(q - e['t']) < 1e-3, e
    e['t'] = round(q, 4)

CUES = {'shots': shots, 'c': C, 'lit': lit, 'phonesOff': phones_off, 'grid': 0.3, 'duration': DUR}
with open(os.path.join(ROOT, 'film', 'data.js'), 'w') as f:
    f.write('window.TL=' + json.dumps(TL, ensure_ascii=False) + ';\n')
    f.write('window.CUES=' + json.dumps(CUES, ensure_ascii=False) + ';\n')
json.dump(sfx, open(os.path.join(ROOT, 'audio', 'sfx_events.json'), 'w'), indent=0)
print(len(sfx), 'sfx events;', ' '.join(f'{k}={v}' for k, v in C.items() if k not in ('steps',)), 'steps', C['steps'])
