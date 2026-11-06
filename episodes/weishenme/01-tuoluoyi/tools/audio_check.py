import subprocess, numpy as np, sys
f = sys.argv[1] if len(sys.argv) > 1 else "audio/mix.wav"
raw = subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar","48000","-f","f32le","-"],capture_output=True).stdout
x = np.frombuffer(raw, np.float32); sr = 48000
win = int(0.25*sr); n = len(x)//win
rms = [20*np.log10(np.sqrt(np.mean(x[i*win:(i+1)*win]**2))+1e-9) for i in range(n)]
print("RMS dBFS per 0.25 s (one row per 2 s bar):")
for b in range(0, n, 8): print(f"{b*0.25:5.1f}s " + " ".join(f"{v:6.1f}" for v in rms[b:b+8]))
X = np.abs(np.fft.rfft(x)); fr = np.fft.rfftfreq(len(x), 1/sr)
bands = [(20,120),(120,500),(500,2000),(2000,8000),(8000,20000)]
tot = X[(fr>20)].sum()
print("band energy share:", ", ".join(f"{a}-{b}Hz {100*X[(fr>=a)&(fr<b)].sum()/tot:.0f}%" for a,b in bands))
