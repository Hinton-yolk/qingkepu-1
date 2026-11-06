"""Generate the voice-over line by line with edge-tts, keep word timings,
then lay the lines on the 8th-note grid of the score (100 BPM -> 0.3 s).

out: voice/<id>.wav, voice/voice.wav (all lines placed), voice/timeline.json
"""
import asyncio, json, ssl, subprocess, sys, os
import numpy as np, soundfile as sf
import edge_tts, edge_tts.communicate as ec

ec._SSL_CTX = ssl.create_default_context(cafile='/root/.ccr/ca-bundle.crt')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
BPM = 100
GRID = 60 / BPM / 2          # 8th note = 0.3 s
LEAD = 0.6                   # first line starts here (eye opens first)

cfg = json.load(open(os.path.join(ROOT, 'script.json')))


async def tts(line):
    mp3 = os.path.join(ROOT, 'voice', line['id'] + '.mp3')
    wav = os.path.join(ROOT, 'voice', line['id'] + '.wav')
    words = []
    if not os.path.exists(mp3) or '--fresh' in sys.argv:
        c = edge_tts.Communicate(line['text'], cfg['voice'], rate=cfg['rate'], boundary='WordBoundary')
        with open(mp3, 'wb') as f:
            async for ch in c.stream():
                if ch['type'] == 'audio':
                    f.write(ch['data'])
                elif ch['type'] == 'WordBoundary':
                    words.append({'w': ch['text'], 't0': ch['offset'] / 1e7, 't1': (ch['offset'] + ch['duration']) / 1e7})
        json.dump(words, open(mp3 + '.json', 'w'), ensure_ascii=False)
    words = json.load(open(mp3 + '.json'))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp3, '-ac', '1', '-ar', str(SR), wav], check=True)
    return wav, words


async def main():
    out = []
    for ln in cfg['lines']:
        out.append(await tts(ln))
    t = LEAD
    lines, total = [], []
    for ln, (wav, words) in zip(cfg['lines'], out):
        a, _ = sf.read(wav)
        # speech span inside the file
        s0 = words[0]['t0']
        s1 = words[-1]['t1']
        start = t  # file start time in the film; speech starts at start + s0
        # put the speech onset on the 8th grid
        onset = np.ceil((start + s0) / GRID - 1e-6) * GRID
        start = onset - s0
        lines.append({'id': ln['id'], 'text': ln['text'], 'file_t': round(start, 4),
                      't0': round(start + s0, 4), 't1': round(start + s1, 4),
                      'words': [{'w': w['w'], 't0': round(start + w['t0'], 4), 't1': round(start + w['t1'], 4)} for w in words]})
        total.append((start, a))
        t = start + s1 + ln['gap']
    dur = t + 0.4
    dur = np.ceil(dur / (GRID * 2)) * GRID * 2   # whole beats
    mix = np.zeros(int(dur * SR) + SR)
    for st, a in total:
        i = int(round(st * SR))
        mix[i:i + len(a)] += a
    mix = mix[:int(dur * SR)]
    sf.write(os.path.join(ROOT, 'voice', 'voice.wav'), mix, SR)
    json.dump({'bpm': BPM, 'grid': GRID, 'duration': round(float(dur), 4), 'lines': lines},
              open(os.path.join(ROOT, 'voice', 'timeline.json'), 'w'), ensure_ascii=False, indent=1)
    for l in lines:
        print(f"{l['id']} {l['t0']:6.2f}-{l['t1']:6.2f} ({l['t1']-l['t0']:4.2f}s) {l['text']}")
    print('duration', dur)

asyncio.run(main())
