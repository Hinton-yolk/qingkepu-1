"""SFX (synthesized, on the measured grid) + score (ducked under the voice) + voice -> audio/mix.wav at -14 LUFS."""
import json, os
import numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.signal import butter, sosfilt, fftconvolve

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
score, _ = sf.read(os.path.join(ROOT, 'audio', 'score.wav'))
voice, _ = sf.read(os.path.join(ROOT, 'voice', 'voice.wav'))
EV = json.load(open(os.path.join(ROOT, 'audio', 'sfx_events.json')))
N = max(len(score), len(voice))
score = np.pad(score, ((0, N - len(score)), (0, 0)))
voice = np.pad(voice, (0, N - len(voice)))
sfx = np.zeros((N, 2))
rng = np.random.default_rng(7)


def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR


def add(sig, t, g=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= N: return
    sig = sig[:N - i] * g
    sfx[i:i + len(sig), 0] += sig * np.cos((pan + 1) * np.pi / 4)
    sfx[i:i + len(sig), 1] += sig * np.sin((pan + 1) * np.pi / 4)


def bell(n, d=2.5):
    t = tt(d); f = mtof(n)
    return (np.sin(2*np.pi*f*t)*np.exp(-t*1.8) + .5*np.sin(2*np.pi*f*2.756*t)*np.exp(-t*3) + .25*np.sin(2*np.pi*f*5.404*t)*np.exp(-t*5)) * np.minimum(1, t/0.002) * .5


def ding():
    t = tt(2.2); f = mtof(88)
    return (np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*f*2.0*t)*np.exp(-t*2) + .12*np.sin(2*np.pi*f*3.01*t)*np.exp(-t*4)) * np.exp(-t*1.6) * np.minimum(1, t/0.001) * .55


def gliss(d, n0=62):
    t = tt(d + 0.6)
    f = mtof(n0) * 2 ** (np.minimum(t, d) / d)
    ph = 2*np.pi*np.cumsum(f)/SR
    env = np.minimum(1, t/0.08) * np.where(t > d, np.exp(-(t-d)/0.15), 1)
    s = np.sin(ph) + .4*np.sin(2*ph) + .2*np.sin(3.01*ph)
    return s * env * .3


def rise(n, d):
    t = tt(d)
    s = sum(np.sin(2*np.pi*mtof(n+k)*t) for k in (0, 7, 12, 19))
    return s * (t/d)**2 * .22


def tick(): t = tt(.04); return np.sin(2*np.pi*4800*t)*np.exp(-t*170)*.5
def pop(n): t = tt(.25); f = mtof(n)*(1+.5*np.exp(-t*60)); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*14)*.6
def blip(n): t = tt(.18); return (np.sin(2*np.pi*mtof(n)*t)+.25*np.sin(4*np.pi*mtof(n)*t))*np.exp(-t*26)*.5
def pluck(n):
    t = tt(1.0); f = mtof(n)
    return sum(a*np.sin(2*np.pi*f*k*t)*np.exp(-t*(3+2.4*k)) for k, a in [(1, 1), (2, .45), (3, .2), (4, .1)])*np.minimum(1, t/.003)*.5
def ting(n): t = tt(1.2); f = mtof(n); return (np.sin(2*np.pi*f*t)*np.exp(-t*4)+.6*np.sin(2*np.pi*f*2.76*t)*np.exp(-t*7)+.3*np.sin(2*np.pi*f*5.4*t)*np.exp(-t*11))*.4
def off(n): t = tt(.2); f = mtof(n)*(1-.4*t/.2); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*20)*.5


for i, e in enumerate(EV):
    k, t, g = e['k'], e['t'], e['g']
    pan = ((i * 0.37) % 1 - 0.5) * 0.6
    sig = {'bell': lambda: bell(e.get('n', 74)), 'ding': ding, 'gliss': lambda: gliss(e.get('d', .8)),
           'rise': lambda: rise(e.get('n', 62), e.get('d', 1)), 'tick': tick, 'pop': lambda: pop(e['n']),
           'blip': lambda: blip(e['n']), 'pluck': lambda: pluck(e['n']), 'ting': lambda: ting(e['n']),
           'off': lambda: off(e['n'])}[k]()
    add(sig, t, g, pan)

# small room on the sfx
ir_t = tt(1.2)
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 5)
ir = sosfilt(butter(2, 5000/(SR/2), output='sos'), ir); ir /= np.sqrt((ir**2).sum())
sfx = sfx + 0.25 * np.stack([fftconvolve(sfx[:, c], ir)[:N] for c in range(2)], 1)

# voice: gentle presence + de-boom, slight compression
v = sosfilt(butter(2, 90/(SR/2), 'highpass', output='sos'), voice)
env = np.sqrt(np.convolve(v**2, np.ones(int(.02*SR))/int(.02*SR), 'same'))
gain = 1 / np.maximum(1, (env / (np.percentile(env[env > 1e-4], 90) * 0.8)) ** 0.5)
v = v * gain

# duck the score under the voice (attack 40 ms, release 350 ms)
act = np.convolve(np.abs(voice) > 0.01, np.ones(int(.05*SR)), 'same') > 0
duck = np.zeros(N); a_att, a_rel = np.exp(-1/(.04*SR)), np.exp(-1/(.35*SR)); y = 0.0
step = 64
for i in range(0, N, step):
    target = 1.0 if act[i] else 0.0
    c = a_att if target > y else a_rel
    y = target + (y - target) * c ** step
    duck[i:i+step] = y
score_g = 1 - 0.28 * duck         # about -3 dB under speech: the music stays present

meter = pyln.Meter(SR)
lv = meter.integrated_loudness(v[v != 0] if np.any(v) else v)
v *= 10 ** ((-16 - lv) / 20)
ls = meter.integrated_loudness(score)
score *= 10 ** ((-17.5 - ls) / 20)
sfx *= 10 ** ((-22 - meter.integrated_loudness(sfx)) / 20)

mix = score * score_g[:, None] + sfx + v[:, None]
L = meter.integrated_loudness(mix)
mix *= 10 ** ((-14 - L) / 20)
# soft limiter to -1 dBTP-ish
lim = 10 ** (-1.2 / 20)
mix = np.where(np.abs(mix) > lim * 0.8, np.sign(mix) * (lim * 0.8 + (lim * 0.2) * np.tanh((np.abs(mix) - lim * 0.8) / (lim * 0.2))), mix)
L2 = meter.integrated_loudness(mix)
mix *= 10 ** ((-14 - L2) / 20)
sf.write(os.path.join(ROOT, 'audio', 'mix.wav'), mix, SR, subtype='PCM_24')
sf.write(os.path.join(ROOT, 'audio', 'stem_sfx.wav'), sfx, SR)
print(f'mix: {meter.integrated_loudness(mix):.2f} LUFS, peak {20*np.log10(np.abs(mix).max()):.2f} dBFS, {len(mix)/SR:.2f}s')
# the loudest 100 ms window of the score+sfx (voice excluded): where does the payoff land?
ms = score * score_g[:, None] + sfx
w = int(.1 * SR); rms = np.sqrt(np.convolve((ms**2).mean(1), np.ones(w)/w, 'valid'))
hit = json.load(open(os.path.join(ROOT, 'voice', 'timeline.json')))['shots']['S12']
print(f'loudest music moment: {np.argmax(rms)/SR:.2f}s (payoff hit is at {hit:.2f}s)')

# what a phone speaker plays: nothing below ~300 Hz. Compare music and voice in that band, while the voice speaks.
from scipy.signal import butter as _b, sosfilt as _f
hpf = lambda x: _f(_b(4, 300 / (SR / 2), 'highpass', output='sos'), x, axis=0)
mus = hpf((score * score_g[:, None] + sfx).mean(1)); voc = hpf(v)
m_speech = act > 0
r = lambda x: 10 * np.log10(np.mean(x[m_speech] ** 2) + 1e-12)
print(f'phone band (>300 Hz) while speaking: music {r(mus) - r(voc):+.1f} dB relative to the voice')
