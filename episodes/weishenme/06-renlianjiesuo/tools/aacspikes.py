# aacspikes.py SOURCE.wav ENCODED.mp4 — finds AAC encoder spikes (10 ms windows louder than the source); the default
# ffmpeg AAC coder (twoloop) can add +5–8 dB clicks on transients, so render.mjs encodes with -aac_coder fast.
# worst 10 ms windows where the decoded AAC exceeds the source peak (encoder spikes)
import sys, subprocess, numpy as np
def load(f): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","2","-ar","48000","-f","f32le","-"],capture_output=True).stdout, np.float32).reshape(-1,2)
a, b = load(sys.argv[1]), load(sys.argv[2]); n = min(len(a), len(b)); w = 480
# AAC has an encoder delay; align by cross-correlating the first 5 s
seg = 48000*5; c = np.correlate(b[:seg+2048,0], a[:seg,0], "valid"); d = int(np.argmax(c)); b = b[d:d+n]; n = min(len(a), len(b))
pa = np.abs(a[:n//w*w]).reshape(-1, w, 2).max(axis=(1,2)); pb = np.abs(b[:n//w*w]).reshape(-1, w, 2).max(axis=(1,2))
r = 20*np.log10((pb+1e-9)/(pa+1e-9)); bad = np.where((r > 1.0) & (pb > 0.3))[0]
loud = pb > 0.3; rl = np.where(loud, r, -99)   # only windows loud enough to hear (silence would make the ratio meaningless)
print(f"delay {d} samples; audible windows overshooting the source by >1 dB: {len(bad)}; worst {rl.max():.1f} dB at {rl.argmax()*0.01:.2f} s")
