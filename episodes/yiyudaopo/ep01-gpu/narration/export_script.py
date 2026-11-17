#!/usr/bin/env python3
"""从 remotion/src/timing.json 生成 narration/旁白与时间轴.md 和 narration/EP01_Pilot_v01.srt（和成片同一个时间源）"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); EP = os.path.dirname(HERE)
T = json.load(open(os.path.join(EP, 'remotion', 'src', 'timing.json')))
N = {l['id']: l for l in json.load(open(os.path.join(HERE, 'narration.json')))['lines']}
SEQ = {'A': 'A 钩子', 'B': 'B GPU 为什么而造', 'C': 'C AI 实际在算什么', 'D': 'D 揭晓', 'E': 'E 通往下一个问题'}
ts = lambda s: f'{int(s // 60)}:{s % 60:05.2f}'
md = [f"# EP01 开头旁白与时间轴（{T['version']}）", '',
      f"- 配音：{'Piper 本地临时 TTS（zh_CN-huayan-medium），不是终版声音' if T['engine'] == 'piper' else T['engine']}",
      f"- 总长 {T['total']:.1f} 秒（成片多留 0.4 秒）；时间是每句在成片里的起止。",
      '- **这一稿不是导演说的 V2.1**：V2.1 在仓库和 Google Drive 里都没找到，按任务书 A–E 五段重写。拿到 V2.1 后改 `narration.json` 的 text，跑 `tts.py`，画面里的动作按句子 id 自动跟着移。', '']
cur = None
for l in T['lines']:
    if l['seq'] != cur:
        cur = l['seq']; a, b = T['seqs'][cur]; md += ['', f"## {SEQ[cur]}（{ts(a)}–{ts(b)}）", '', '| id | 起 | 止 | 旁白 | 句后停顿 |', '|---|---|---|---|---|']
    md.append(f"| {l['id']} | {ts(l['start'])} | {ts(l['end'])} | {l['text']} | {N[l['id']]['pause']} s |")
open(os.path.join(HERE, '旁白与时间轴.md'), 'w').write('\n'.join(md) + '\n')
srt = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round(s % 1 * 1000)) % 1000:03d}"
out = []
for i, l in enumerate(T['lines'], 1): out += [str(i), f"{srt(l['start'])} --> {srt(l['end'])}", l['text'], '']
open(os.path.join(HERE, 'EP01_Pilot_v01.srt'), 'w').write('\n'.join(out))
print('ok')
