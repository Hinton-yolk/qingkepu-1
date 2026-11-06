"""Lay the Fish Audio voice lines onto the existing cut.
Each line keeps the speech onset of the cut (so every shot, cue and score section stays valid);
word times are carried over from the old timing through a piecewise-linear map anchored on the
pauses the new voice actually makes at the punctuation. A line that would run into the next one
is sped up slightly (atempo, at most 1.18x).
out: voice/voice.wav, voice/timeline.json (same schema as before)"""
import json, os, subprocess, io
import numpy as np, soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
OLD = json.load(open(os.path.join(ROOT, 'voice', 'timeline_edge.json')))
FISH = os.path.join(ROOT, 'voice', 'fish')
PUNCT = '，。：；？、！'


def load(path, tempo=1.0):
    af = ['-af', f'atempo={tempo:.4f}'] if abs(tempo - 1) > 1e-3 else []
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', path, *af, '-ac', '1', '-ar', str(SR), '-f', 'wav', '-'], capture_output=True, check=True).stdout
    a, _ = sf.read(io.BytesIO(raw))
    return a / (np.abs(a).max() + 1e-9) * 0.89


def speech(a):
    hop = 480  # 10 ms
    n = len(a) // hop
    e = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1))
    db = 20 * np.log10(e + 1e-9)
    on = db > -42
    idx = np.where(on)[0]
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


def spans(text, words):
    pos, out = 0, []
    for w in words:
        j = text.find(w['w'], pos)
        if j < 0:
            j = pos
        out.append((j, j + len(w['w'])))
        pos = j + len(w['w'])
    return out


lines, placed = [], []
olines = OLD['lines']
for k, L in enumerate(olines):
    path = os.path.join(FISH, L['id'] + '.mp3')
    nxt = olines[k + 1]['t0'] if k + 1 < len(olines) else OLD['duration'] - 1.6
    room = nxt - 0.14 - L['t0']
    tempo = 1.0
    a = load(path)
    s0, s1, pauses = speech(a)
    if s1 - s0 > room:
        tempo = min(1.18, (s1 - s0) / room)
        a = load(path, tempo)
        s0, s1, pauses = speech(a)
    start = L['t0'] - s0            # file start time in the film
    n0, n1 = L['t0'], L['t0'] + (s1 - s0)
    # anchors: old pause edges -> new pause edges, at the punctuation inside the line
    text, words = L['text'], L['words']
    sp = spans(text, words)
    cuts = []   # (old_end_before, old_start_after)
    for ci, ch in enumerate(text):
        if ch in PUNCT and ci < len(text.rstrip(PUNCT)) :
            before = [w for w, (a0, a1) in zip(words, sp) if a1 <= ci]
            after = [w for w, (a0, a1) in zip(words, sp) if a0 > ci]
            if before and after:
                cuts.append((before[-1]['t1'], after[0]['t0']))
    anchors = [(L['t0'], n0)]
    lin = lambda t: n0 + (t - L['t0']) / max(1e-6, L['t1'] - L['t0']) * (n1 - n0)
    used, hits = set(), 0
    for ob, oa in cuts:                       # each punctuation gets the detected pause nearest its linear guess
        guess = lin((ob + oa) / 2)
        cand = [(abs(start + (p0 + p1) / 2 - guess), i) for i, (p0, p1) in enumerate(pauses) if i not in used]
        if cand:
            d, i = min(cand)
            if d < 0.55:
                used.add(i); hits += 1
                p0, p1 = pauses[i]
                anchors += [(ob, start + p0), (oa, start + p1)]
    mode = f'{hits}/{len(cuts)} matched'
    anchors.append((L['t1'], n1))
    anchors.sort()
    ox = np.array([x for x, _ in anchors]); ny = np.array([y for _, y in anchors])
    ny = np.maximum.accumulate(ny)
    M = lambda t: float(np.interp(t, ox, ny))
    nw = [{'w': w['w'], 't0': round(M(w['t0']), 4), 't1': round(M(w['t1']), 4)} for w in words]
    lines.append({'id': L['id'], 'text': text, 'file_t': round(start, 4), 't0': round(n0, 4), 't1': round(n1, 4), 'words': nw})
    placed.append((start, a))
    print(f"{L['id']} old {L['t1']-L['t0']:4.2f}s new {n1-n0:4.2f}s room {room:4.2f}s tempo {tempo:.3f} {mode:7s} pauses {len(pauses)}/{len(cuts)}")

dur = OLD['duration']
mix = np.zeros(int(dur * SR) + SR)
for st, a in placed:
    i = int(round(st * SR))
    mix[i:i + len(a)] += a[:max(0, len(mix) - i)]
mix = mix[:int(dur * SR)]
sf.write(os.path.join(ROOT, 'voice', 'voice.wav'), mix, SR)
json.dump({'bpm': OLD['bpm'], 'grid': OLD['grid'], 'duration': dur, 'voice': 'Fish Audio · 科普 (83bc284d2a3848c8a37f6d9a9ab11cd8)', 'lines': lines},
          open(os.path.join(ROOT, 'voice', 'timeline.json'), 'w'), ensure_ascii=False, indent=1)
print('voice.wav written,', dur, 's')
