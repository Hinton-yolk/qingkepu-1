"""v2 layout: 16 lines of the Fish 「科普」 voice, shot times derived from the voice.
Lines kept from v1 reuse their pause-anchored word times; new lines get character times
spread across the speech chunks between the pauses the voice actually makes.
out: voice/voice.wav, voice/timeline.json (+ 'shots')"""
import json, os, subprocess, io, math
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, G8, BEAT = 48000, 0.3, 0.6
V1 = {l['id']: l for l in json.load(open(os.path.join(ROOT, 'voice', 'timeline_fish_v1.json')))['lines']}
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


# id, text, audio, v1 id (reuse words) or None
LINES = [
    ('L01', 'L01'), ('L02', 'L02'), ('L03', 'L03'), ('L04', 'L04'), ('L05', 'L05'), ('L06', 'L06'), ('L07', 'L07'), ('L08', 'L08'),
    ('L09', ('N09', '凑近看：它会被墙削弱，被人体吸收，也会被金属反射。')),
    ('L10', 'L14'), ('L11', 'L15'),
    ('L12', ('N12', '想看得和现在一样清楚，瞳孔得大到离谱：差不多要半公里。')),
    ('L13', ('N13', '巧的是，人类真造过这么大的一只“眼睛”：中国天眼，口径500米，专门收听宇宙里的无线电。')),
    ('L14', ('N14', '所以它最怕的，就是我们身边的手机和 Wi-Fi：方圆5公里，一律禁用。')),
    ('L15', ('N15', '当然，真实世界不会这么整齐：它们会反射、叠加、绕射——整座城市，都泡在看不见的电磁波里。')),
    ('L16', 'L19'),
]
audio, info = {}, {}
for nid, src in LINES:
    if isinstance(src, str):
        L = V1[src]
        a = load(os.path.join(FISH, src + '.mp3'))
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
for i, nid in enumerate(['L01', 'L02', 'L03', 'L04', 'L05', 'L06', 'L07', 'L08']):
    onset[nid] = V1[LINES[i][1]]['t0']
shots.update(S01=0.0, S02=4.8, S03=8.4, S04=16.2, S05=25.8, S06=35.4)
end = lambda nid: onset[nid] + info[nid]['dur']
onset['L09'] = 35.7
shots['S09'] = up(end('L09') + 1.3)              # bad news: hold the block, silence
onset['L10'] = shots['S09'] + 0.6
shots['S10'] = shots['S09'] + 3.0                # blur -> small eye
onset['L11'] = shots['S10'] + 0.3
shots['S11'] = up(end('L11') + 0.4)              # the pupil you would need
onset['L12'] = shots['S11'] + 0.3
shots['S12'] = up(end('L12') + 0.7)              # PAYOFF hit: FAST
onset['L13'] = shots['S12'] + 0.9
shots['S13'] = up(end('L13') + 0.5)              # the 5 km quiet zone
onset['L14'] = shots['S13'] + 0.3
shots['S14'] = up(end('L14') + 0.6)              # the real world: a city soaked in a messy field
onset['L15'] = shots['S14'] + 0.6
shots['S15'] = up(end('L15') + 1.8)              # back to the eye
onset['L16'] = shots['S15'] + 0.6
dur = up(end('L16') + 2.4)
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
