"""v2 layout: 16 lines of the Fish 「科普」 voice, shot times derived from the voice.
Lines kept from v1 reuse their pause-anchored word times; new lines get character times
spread across the speech chunks between the pauses the voice actually makes.
out: voice/voice.wav, voice/timeline.json (+ 'shots')"""
import json, os, subprocess, io, math
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, G8, BEAT = 48000, 0.3, 0.6
V1 = {l['id']: l for l in json.load(open(os.path.join(ROOT, 'voice', 'timeline_v2.json')))['lines']}
FILE = {'L01': 'L01', 'L02': 'L02', 'L10': 'L14', 'L11': 'L15', 'L12': 'N12', 'L16': 'L19'}
FISH = os.path.join(ROOT, 'voice', 'fish')
PUNCT = '，。：；？、！—“”'

up = lambda t, g=BEAT: math.ceil(t / g - 1e-6) * g
r4 = lambda x: round(x, 4)


def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'wav', '-'], capture_output=True, check=True).stdout
    a, _ = sf.read(io.BytesIO(raw))
    return a / (np.abs(a).max() + 1e-9) * 0.89


def speech(a):
    hop = 480
    n = len(a) // hop
    db = 20 * np.log10(np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    idx = np.where(db > -42)[0]
    s0, s1 = idx[0], idx[-1] + 1
    pauses, run = [], None
    for i in range(s0, s1):
        if db[i] < -31:
            run = i if run is None else run
        else:
            if run is not None and i - run >= 6:
                pauses.append((run * hop / SR, i * hop / SR))
            run = None
    return s0 * hop / SR, s1 * hop / SR, pauses


def char_words(text, s0, s1, pauses):
    """character timings for a new line: chunks between punctuation <- speech between matched pauses"""
    chunks, cur = [], ''
    for ch in text:
        if ch in PUNCT:
            if cur.strip(): chunks.append(cur.strip())
            cur = ''
        else:
            cur += ch
    if cur.strip(): chunks.append(cur.strip())
    n = len(chunks)
    lens = np.array([len(c.replace(' ', '')) for c in chunks], float)
    # expected boundaries by character share, then snap each to the nearest detected pause
    total = s1 - s0
    exp = s0 + np.cumsum(lens)[:-1] / lens.sum() * total
    used, segs, prev = set(), [], s0
    bounds = []
    for e in exp:
        cand = [(abs((p0 + p1) / 2 - e), i) for i, (p0, p1) in enumerate(pauses) if i not in used and p0 > prev]
        if cand and min(cand)[0] < 0.6:
            _, i = min(cand); used.add(i); bounds.append(pauses[i]); prev = pauses[i][1]
        else:
            bounds.append((e - 0.05, e + 0.05)); prev = e
    starts = [s0] + [b[1] for b in bounds]
    ends = [b[0] for b in bounds] + [s1]
    words = []
    for c, a0, a1 in zip(chunks, starts, ends):
        cs = c.replace(' ', '')
        for k, ch in enumerate(cs):
            words.append({'w': ch, 't0': a0 + (a1 - a0) * k / len(cs), 't1': a0 + (a1 - a0) * (k + 1) / len(cs)})
    return words


LINES = [
    ('L01', 'L01'), ('L02', 'L02'),
    ('L04', ('SW', 'Wi-Fi 的波长有12厘米，差不多就是你手机那么长。')),
    ('L05', ('SR', '在 Wi-Fi 眼里，路由器是一盏从不关的灯：没人上网，它也每秒闪约十次。')),
    ('L08', ('SB', '墙也挡不住它：隔壁、楼上、楼下，整栋楼一闪一闪，像万家灯火。')),
    ('L10', 'L10'), ('L11', 'L11'), ('L12', 'L12'),
    ('L13', ('SF', '巧的是，人类真造过这么大的一只“眼睛”：中国天眼，口径500米。')),
    ('L14', ('SQ', '而它最怕的，恰恰就是手机和 Wi-Fi。')),
    ('L15', ('SC', '真实世界更乱：整座城市，都泡在看不见的电磁波里。')),
    ('L16', 'L16'),
]
audio, info = {}, {}
for nid, src in LINES:
    if isinstance(src, str):
        L = V1[src]
        a = load(os.path.join(FISH, FILE[src] + '.mp3'))
        s0, s1, _ = speech(a)
        rel = [{'w': w['w'], 't0': w['t0'] - L['t0'], 't1': w['t1'] - L['t0']} for w in L['words']]
        info[nid] = dict(text=L['text'], a=a, s0=s0, dur=s1 - s0, rel=rel)
    else:
        fid, text = src
        a = load(os.path.join(FISH, fid + '.mp3'))
        s0, s1, pauses = speech(a)
        cw = char_words(text, s0, s1, pauses)
        rel = [{'w': w['w'], 't0': w['t0'] - s0, 't1': w['t1'] - s0} for w in cw]
        info[nid] = dict(text=text, a=a, s0=s0, dur=s1 - s0, rel=rel)

onset, shots = {}, {}
up8 = lambda t: up(t, G8)
end = lambda nid: onset[nid] + info[nid]['dur']
shots['S01'] = 0.0
onset['L01'] = 0.3
shots['S02'] = 2.1                                # pupil push 1.5-2.1, vision switch at 2.4
onset['L02'] = up8(end('L01') + 0.4)
shots['S03'] = up(end('L02') + 0.2)               # 12 cm
onset['L04'] = shots['S03'] + 0.3
shots['S04'] = up(end('L04') + 0.5)               # the router
onset['L05'] = shots['S04'] + 0.3
shots['S05'] = up(end('L05') + 0.4)               # the building
onset['L08'] = shots['S05'] + 0.3
shots['S09'] = up(end('L08') + 1.5)               # bad news
onset['L10'] = shots['S09'] + 0.6
shots['S10'] = shots['S09'] + 2.4                 # blur -> small eye
onset['L11'] = shots['S10'] + 0.3
shots['S11'] = up(end('L11') + 0.3)               # the pupil you would need
onset['L12'] = shots['S11'] + 0.3
shots['S12'] = up(end('L12') + 0.6)               # PAYOFF: FAST
onset['L13'] = shots['S12'] + 0.9
shots['S13'] = up(end('L13') + 0.3)               # the quiet zone
onset['L14'] = shots['S13'] + 0.3
shots['S14'] = up(end('L14') + 0.6)               # the city
onset['L15'] = shots['S14'] + 0.6
shots['S15'] = up(end('L15') + 1.5)               # back to the eye
onset['L16'] = shots['S15'] + 0.6
dur = up(end('L16') + 2.1)
for k in onset:                                   # speech onsets on the 8th grid
    onset[k] = round(math.ceil(onset[k] / G8 - 1e-6) * G8, 4)

lines = []
mix = np.zeros(int(dur * SR) + SR)
for nid, _ in LINES:
    I = info[nid]
    t0 = onset[nid]
    st = t0 - I['s0']
    i = int(round(st * SR)); mix[i:i + len(I['a'])] += I['a'][:max(0, len(mix) - i)]
    lines.append({'id': nid, 'text': I['text'], 'file_t': r4(st), 't0': r4(t0), 't1': r4(t0 + I['dur']),
                  'words': [{'w': w['w'], 't0': r4(t0 + w['t0']), 't1': r4(t0 + w['t1'])} for w in I['rel']]})
mix = mix[:int(dur * SR)]
sf.write(os.path.join(ROOT, 'voice', 'voice.wav'), mix, SR)
json.dump({'bpm': 100, 'grid': G8, 'duration': r4(dur), 'voice': 'Fish Audio · 科普 (83bc284d2a3848c8a37f6d9a9ab11cd8)',
           'shots': {k: r4(v) for k, v in shots.items()}, 'lines': lines},
          open(os.path.join(ROOT, 'voice', 'timeline.json'), 'w'), ensure_ascii=False, indent=1)
for l in lines: print(f"{l['id']} {l['t0']:6.2f}-{l['t1']:6.2f}  {l['text']}")
print('shots', {k: round(v, 2) for k, v in shots.items()}, 'duration', dur)
