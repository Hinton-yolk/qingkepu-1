#!/usr/bin/env python3
"""临时配音：Piper（本地、免费、MIT）zh_CN-huayan-medium，一句一个 wav，统一到 -20 LUFS，
再按 narration.json 的停顿排出时间轴，写到 remotion/public/vo/ 和 remotion/src/timing.json。

  python3 tts.py [--voices <放 .onnx 的目录>] [--engine piper|files]

--engine files：不合成，直接用 vo_src/<id>.wav（以后换成 Fish Audio 或真人录音时用：把每句的 wav 放进去即可）。
声线 onnx 不进仓库，从 huggingface.co/rhasspy/piper-voices 下载 zh/zh_CN/huayan/medium/。
"""
import json, os, re, subprocess, sys, wave

HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(HERE)
PUB = os.path.join(EP, 'remotion', 'public', 'vo')
SRC_TIMING = os.path.join(EP, 'remotion', 'src', 'timing.json')
RAW = os.path.join(HERE, 'vo_src')
LEAD_IN = 0.15          # 片头第一句前留的时间（秒）
TEMPO = 1.03            # 后期整体略提速（不变调），把总长收进 100 秒
LENGTH_SCALE = 0.92     # Piper 默认约 6 字/秒，略放慢到约 5.3 字/秒

# espeak 读英文缩写会乱读，这里只在「念」的时候替换，字幕仍然用原文
SAY = [('GPU', 'G P U'), ('CPU', 'C P U'), ('AI', 'A I'), ('「', ''), ('」', '')]

def arg(k, d=None):
    a = sys.argv; return a[a.index(k) + 1] if k in a else d

def dur(p):
    with wave.open(p) as w: return w.getnframes() / w.getframerate()

def main():
    N = json.load(open(os.path.join(HERE, 'narration.json')))
    voices = arg('--voices', os.environ.get('PIPER_VOICES', ''))
    engine = arg('--engine', 'piper')
    os.makedirs(PUB, exist_ok=True); os.makedirs(RAW, exist_ok=True)
    t = LEAD_IN; out = []
    for L in N['lines']:
        raw = os.path.join(RAW, L['id'] + '.wav'); dst = os.path.join(PUB, L['id'] + '.wav')
        if engine == 'piper':
            say = L.get('say', L['text'])
            for a, b in SAY: say = say.replace(a, b)
            subprocess.run([sys.executable, '-m', 'piper', '-m', os.path.join(voices, 'zh_CN-huayan-medium.onnx'),
                            '-f', raw, '--length-scale', str(L.get('ls', LENGTH_SCALE)), '--sentence-silence', '0'],
                           input=say.encode(), check=True, capture_output=True)
        # 去掉首尾静音 → 48 kHz 单声道 → -20 LUFS
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af',
                        'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,'
                        f"atempo={L.get('tempo', TEMPO)},loudnorm=I=-20:TP=-2:LRA=7,aresample=48000", '-ac', '1', dst], check=True)
        d = dur(dst)
        out.append(dict(id=L['id'], seq=L['seq'], text=L['text'], start=round(t, 3), end=round(t + d, 3), file=f"vo/{L['id']}.wav"))
        t += d + L['pause']
    total = round(t, 3)
    seqs = {}
    for o in out: seqs.setdefault(o['seq'], [o['start'], o['end']]); seqs[o['seq']][1] = o['end']
    src_note = os.path.join(RAW, 'SOURCE.txt')
    if engine == 'piper': open(src_note, 'w').write('piper')
    label = open(src_note).read().strip() if os.path.exists(src_note) else engine
    json.dump(dict(version=N['version'], engine=label, total=total, lines=out, seqs=seqs), open(SRC_TIMING, 'w'), ensure_ascii=False, indent=1)
    for o in out: print(f"{o['id']:3s} {o['start']:6.2f}–{o['end']:6.2f}  {len(re.sub(r'[^一-龥A-Za-z0-9]', '', o['text'])) / (o['end'] - o['start']):.1f} 字/秒  {o['text']}")
    print('总长', total, '秒'); print({k: (round(v[0], 1), round(v[1], 1)) for k, v in seqs.items()})

if __name__ == '__main__':
    main()
