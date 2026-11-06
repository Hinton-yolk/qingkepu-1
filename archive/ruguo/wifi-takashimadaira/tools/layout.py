"""The one timeline. Places the nine Fish 「科普」 lines on a 120 BPM grid, finds where each subtitle part starts from the
pauses the voice actually makes, and names every visual / musical hit by its beat.
out: timeline.json (read by main.js, score.py, sfx + mix.py, srt), voice/voice.wav, cues.json"""
import json, os, subprocess, io
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, BPM = 48000, 120
BEAT = 60 / BPM
DUR = 46.0
L = {l['id']: l for l in json.load(open(os.path.join(ROOT, 'voice', 'lines.json')))}
# where each line's speech starts (seconds); chosen so the key word lands on the hit named next to it
ONSET = {'L01': 0.40, 'L02': 5.00, 'L03': 9.50, 'L04': 13.50, 'L05': 18.50, 'L06': 24.50, 'L07': 28.00, 'L08': 34.00, 'L09': 36.60}
# hits, in beats (×0.5 s). These are the only times the picture and the score agree on.
HIT = {
    'first':      0,    # one window already on at frame 0
    'cascade':    7,    # 3.5  「会是这样」: the whole facade has caught
    'crane':      9,    # 4.5  crane up and back begins
    'pin':        13,   # 6.5  「一栋板楼」: pin drops on the slab
    'readout1':   19,   # 9.5  readout 01 arrives
    'count1':     24,   # 12.0 「两百多台」: counter lands on 210
    'readout2':   29,   # 14.5 readout 02 (beacons)
    'count2':     33,   # 16.5 「十次」: counter lands on 10
    'here':       35,   # 17.5 「我在这儿」: one window calls, one ring
    'boom':       37,   # 18.5 boom down toward the ground
    'spill':      41,   # 20.5 「穿过墙」: rings leave the slab
    'n1':         50,   # 25.0 「隔壁那栋」
    'n2':         52,   # 26.0 「再隔壁」
    'spread':     56,   # 28.0 everything starts switching on outward
    'all':        60,   # 30.0 「六千多台」: the last building on; heaviest hit
    'lightsup':   67,   # 33.5 house lights up, projector off: 「你看不见它们」
    'lamp':       72,   # 36.0 house lights down, the lamp strikes: the turn
    'glow':       77,   # 38.5 「万家灯火」
    'card':       80,   # 40.0 end card
    'end':        92,   # 46.0
}
T = {k: v * BEAT for k, v in HIT.items()}


def load(path):
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'wav', '-'], capture_output=True, check=True).stdout
    a, _ = sf.read(io.BytesIO(raw))
    return a / (np.abs(a).max() + 1e-9) * 0.89


def envelope(a, hop=480):
    n = len(a) // hop
    return 20 * np.log10(np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9), hop / SR


def segments(a):
    db, dt = envelope(a)
    on = db > -40
    idx = np.where(on)[0]
    s0, s1 = idx[0], idx[-1] + 1
    pauses, run = [], None
    for i in range(s0, s1):
        if db[i] < -34:
            run = i if run is None else run
        else:
            if run is not None and i - run >= 8:
                pauses.append(((run) * dt, i * dt))
            run = None
    return s0 * dt, s1 * dt, pauses


voice = np.zeros(int(DUR * SR))
lines, cues = [], []
for lid, t_on in ONSET.items():
    a = load(os.path.join(ROOT, 'voice', 'fish', f'{lid}.wav'))
    s0, s1, pauses = segments(a)
    start = t_on - s0                                  # file start so speech begins at t_on
    i0 = int(round(start * SR))
    voice[i0:i0 + len(a)] += a[:max(0, min(len(a), len(voice) - i0))]
    subs = L[lid]['sub']
    # subtitle boundaries: the pause closest to where the characters say it should be
    n = [len(s.replace(' ', '')) for s in subs]
    bounds, used = [], set()
    for k in range(1, len(subs)):
        want = s0 + (s1 - s0) * sum(n[:k]) / sum(n)
        cand = [(abs((p0 + p1) / 2 - want), j) for j, (p0, p1) in enumerate(pauses) if j not in used]
        j = min(cand)[1] if cand else None
        if j is None: bounds.append(want); continue
        used.add(j); bounds.append(pauses[j])
    edges = [(s0, None)] + [(b[1], b[0]) if isinstance(b, tuple) else (b, b) for b in bounds] + [(None, s1)]
    parts = []
    for k, text in enumerate(subs):
        a0 = edges[k][0]; a1 = edges[k + 1][1]
        parts.append(dict(text=text, on=round(start + a0, 3), off=round(start + a1, 3)))
    lines.append(dict(id=lid, start=round(start, 3), on=round(t_on, 3), off=round(start + s1, 3), parts=parts))
    cues += parts

# subtitle holds: on screen from speech start to the next cue, at least max(1.8 s, speech + 0.6 s)
cues.sort(key=lambda c: c['on'])
for k, c in enumerate(cues):
    nxt = cues[k + 1]['on'] - 0.04 if k + 1 < len(cues) else DUR
    c['t0'] = round(max(0, c['on'] - 0.06), 3)
    c['t1'] = round(min(nxt, max(c['t0'] + 1.8, c['off'] + 0.6, c['off'] + 0.35)), 3)
    # a gap of less than half a second between cues reads as flicker: bridge it
    if k + 1 < len(cues) and cues[k + 1]['on'] - 0.06 - c['t1'] < 0.5: c['t1'] = round(cues[k + 1]['on'] - 0.1, 3)

sf.write(os.path.join(ROOT, 'voice', 'voice.wav'), voice.astype(np.float32), SR)
json.dump(dict(bpm=BPM, beat=BEAT, dur=DUR, hit=HIT, t={k: round(v, 3) for k, v in T.items()}, lines=lines, cues=cues),
          open(os.path.join(ROOT, 'timeline.json'), 'w'), ensure_ascii=False, indent=1)
json.dump([dict(t0=c['t0'], t1=c['t1'], text=c['text']) for c in cues], open(os.path.join(ROOT, 'cues.json'), 'w'), ensure_ascii=False, indent=1)
for l in lines:
    print(l['id'], f"{l['on']:6.2f}–{l['off']:6.2f}", ' | '.join(f"{p['text']} {p['on']:.2f}-{p['off']:.2f}" for p in l['parts']))
print('cues', len(cues), ' overlaps:', sum(1 for a, b in zip(cues, cues[1:]) if a['t1'] > b['t0']))
