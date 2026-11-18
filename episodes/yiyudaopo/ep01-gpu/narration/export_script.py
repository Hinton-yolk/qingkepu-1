#!/usr/bin/env python3
"""从 remotion/src/timing.json 生成 narration/旁白与时间轴.md 和 narration/EP01_Full_Assembly_v01.srt（和成片同一个时间源）"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); EP = os.path.dirname(HERE)
T = json.load(open(os.path.join(EP, 'remotion', 'src', 'timing.json')))
N = {l['id']: l for l in json.load(open(os.path.join(HERE, 'narration.json')))['lines']}
SEQ = {'A': 'A 钩子', 'B': 'B 游戏的计算', 'C': 'C AI 的计算', 'D': 'D 揭晓', 'E': 'E 芯片：算得快还不够', 'F': 'F 显存瓶颈', 'G': 'G 一块 GPU 不够', 'H': 'H 下一个瓶颈：芯片之间'}
ts = lambda s: f'{int(s // 60)}:{s % 60:05.2f}'
md = [f"# EP01 开头旁白与时间轴（{T['version']}）", '',
      f"- 配音：{'Piper 本地临时 TTS（zh_CN-huayan-medium），不是终版声音' if T['engine'] == 'piper' else T['engine']}",
      f"- 总长 {T['total']:.1f} 秒（成片多留 0.12 秒）；时间是每句在成片里的起止。",
      '- 旁白文字：A–E 为 Pilot v03 锁定稿（去掉 E2，意思并入 F）；F–H 按导演《FULL EPISODE ASSEMBLY》建议稿（F 段去掉开头三句，避免重复 E 段的问题）。A1、A2、E3、E4、H7、H11 画面上已是大字，不出字幕。改稿时改 `narration.json` 的 text，跑 `tts.py`，画面里的动作按句子 id 自动跟着移。', '']
cur = None
for l in T['lines']:
    if l['seq'] != cur:
        cur = l['seq']; a, b = T['seqs'][cur]; md += ['', f"## {SEQ[cur]}（{ts(a)}–{ts(b)}）", '', '| id | 起 | 止 | 旁白 | 句后停顿 |', '|---|---|---|---|---|']
    md.append(f"| {l['id']} | {ts(l['start'])} | {ts(l['end'])} | {l['text']} | {N[l['id']]['pause']} s |")
open(os.path.join(HERE, '旁白与时间轴_全集v01.md'), 'w').write('\n'.join(md) + '\n')
srt = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round(s % 1 * 1000)) % 1000:03d}"
out = []
for i, l in enumerate(T['lines'], 1): out += [str(i), f"{srt(l['start'])} --> {srt(l['end'])}", l['text'], '']
open(os.path.join(HERE, 'EP01_Full_Assembly_v01.srt'), 'w').write('\n'.join(out))
# 平台上传用：去掉画面上已经是大字的几句（和 remotion/src/Captions.tsx 的 HIDE 一致），免得和大字重复
HIDE = ['A1', 'A2', 'E3', 'E4', 'H7', 'H11']
up = []
for i, l in enumerate([l for l in T['lines'] if l['id'] not in HIDE], 1): up += [str(i), f"{srt(l['start'])} --> {srt(l['end'])}", l['text'], '']
open(os.path.join(HERE, 'EP01_Full_Assembly_v01_上传用.srt'), 'w').write('\n'.join(up))
print('ok')
