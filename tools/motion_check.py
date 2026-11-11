"""Motion check for a rendered film (studio rule, see CLAUDE.md in the kepu-studio repo).
usage: python3 motion_check.py <film.mp4> <name> [--end=<seconds where the end card starts>]
Per-frame mean abs difference on a 135x240 grey copy, resampled to 30 fps (so 60 fps films use the same thresholds; films below 30 fps keep their own rate and the threshold scales). A frame counts as still when the difference is < 0.15 (at 30 fps).
Pass for the body of the film (before the end card): still frames < 15 %, every 5 s window < 30 % still, longest still stretch <= 0.6 s."""
import sys, subprocess, numpy as np
try:
    import librosa  # optional: only used for the music tempo / beat line
except ImportError:
    librosa = None
f, name = sys.argv[1], sys.argv[2]
END = next((float(a.split('=')[1]) for a in sys.argv[3:] if a.startswith('--end=')), None)
w, h = 135, 240
# Films slower than 30 fps (e.g. 24) are analysed at their own frame rate: resampling 24 -> 30 repeats every 5th frame,
# which would count as 20 % "still". The threshold scales with the frame gap (0.15 at 30 fps -> 0.1875 at 24 fps).
r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.strip()
try: n_, d_ = r.split('/'); src_fps = float(n_) / float(d_)
except Exception: src_fps = 30.0
fps = src_fps if src_fps < 29.5 else 30
raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', f, '-vf', f'fps={fps},scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
V = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.float32)
d = np.abs(np.diff(V, axis=0)).mean((1, 2)); t = np.arange(len(d)) / fps
static = d < 0.15 * 30 / fps
runs, cur = [], 0
for i, s in enumerate(static):
    if s: cur += 1
    else:
        if cur: runs.append((cur / fps, (i - cur) / fps)); cur = 0
if cur: runs.append((cur / fps, (len(d) - cur) / fps))
runs.sort(reverse=True)
# change events: peaks in d (local maxima above a high percentile)
thr = np.percentile(d, 92); ev = [t[i] for i in range(1, len(d) - 1) if d[i] > thr and d[i] >= d[i - 1] and d[i] >= d[i + 1]]
ev2 = [e for i, e in enumerate(ev) if i == 0 or e - ev[i - 1] > .25]
gaps = np.diff(ev2) if len(ev2) > 1 else np.array([0.0])
aud = subprocess.run(['ffmpeg','-loglevel','error','-i',f,'-ac','1','-ar','22050','-f','f32le','-'],capture_output=True).stdout; y = np.frombuffer(aud, np.float32).copy(); sr = 22050
if librosa is not None and len(y): tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
else: tempo, beats = np.array([np.nan]), np.array([])
near = [min(abs(b - e) for b in beats) for e in ev2] if len(beats) else []
print(f"{name}: {len(d)/fps:.1f}s | frames with ~no motion {static.mean()*100:.0f}% | longest still stretches " + ', '.join(f"{a:.1f}s@{b:.0f}s" for a, b in runs[:5]))
print(f"   motion median {np.median(d):.2f}  p25 {np.percentile(d,25):.2f} | big-change events {len(ev2)}, median gap {np.median(gaps):.2f}s, p90 gap {np.percentile(gaps,90):.2f}s | music {float(np.atleast_1d(tempo)[0]):.0f} BPM, events within 80 ms of a beat {(np.mean(np.array(near) < .08)*100 if near else float('nan')):.0f}%{'' if librosa else ' (pip install librosa for the beat line)'}")
body = d[:int(END * fps)] if END else d
W5 = int(round(5 * fps)); st = body < .15 * 30 / fps; wins = [st[i:i + W5].mean() for i in range(0, len(st), W5) if len(st[i:i + W5]) >= int(2 * fps)]
longest, cur = 0, 0
for s_ in st: cur = cur + 1 if s_ else 0; longest = max(longest, cur)
worst = [(i * 5, round(w * 100)) for i, w in enumerate(wins) if w >= .3]
ok = st.mean() < .15 and not worst and longest / fps <= .6
print(f"   BODY{' (before ' + str(END) + 's)' if END else ''}: still {st.mean()*100:.0f}% (<15%), longest still {longest/fps:.2f}s (<=0.6s), windows >=30% still: {worst or 'none'} -> {'PASS' if ok else 'FAIL'}")
