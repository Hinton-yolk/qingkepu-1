#!/usr/bin/env python3
"""时间轴检查（Render/QA 用）：镜头首尾相接、旁白落在所属镜头内、语速不超过上限、标注不越界。
用法：python3 timeline/validate.py [--table]   （--table 另外打印 Markdown 时间表）"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, 'timeline.json'), encoding='utf-8'))
fps = T['meta']['fps']; shots = T['shots']; by = {s['id']: s for s in shots}; errs = []; warns = []
def syll(t):
    """估算要念的音节数：汉字 1 个；英文缩写按字母念（GPU = 3，AI = 2，DSP = 3），SerDes 按 2 个；数字 1 个"""
    n = len(re.findall(r'[一-鿿]', t))
    for w in re.findall(r'[A-Za-z]+', t): n += 2 if w.lower() == 'serdes' else len(w)
    return n + len(re.findall(r'\d', t))
for a, b in zip(shots, shots[1:]):
    if abs(a['end'] - b['start']) > 1e-6: errs.append(f"{a['id']} 结束 {a['end']} ≠ {b['id']} 开始 {b['start']}")
for s in shots:
    for v in (s['start'], s['end']):
        if abs(v * fps - round(v * fps)) > 1e-6: errs.append(f"{s['id']} 时间 {v} 不在整帧上")
    for o in s['overlays']:
        if o['t'] < s['start'] - 1e-6 or o['t'] + o['dur'] > s['end'] + 1e-6: errs.append(f"{s['id']} 标注「{o['text'][:10]}」越出镜头")
prev = 0.0; total = 0
for n in T['narration']:
    s = by[n['shot']]; d = n['end'] - n['start']; k = syll(n['text']); total += k; rate = k / d
    if n['start'] < s['start'] or n['end'] > s['end']: errs.append(f"{n['id']} 不在 {s['id']} 内")
    if n['start'] < prev + 0.2: errs.append(f"{n['id']} 和上一句间隔不足 0.2 秒")
    lim = 4.8 if n.get('slow') else 6.2
    if rate > lim: errs.append(f"{n['id']} 语速 {rate:.1f} 字/秒 > {lim}")
    if rate < 3.5: warns.append(f"{n['id']} 语速只有 {rate:.1f} 字/秒，时间偏松")
    prev = n['end']
dur = shots[-1]['end']
print(f"总时长 {dur:.1f} 秒 = {round(dur * fps)} 帧；镜头 {len(shots)} 个；旁白 {len(T['narration'])} 句，约 {total} 字，"
      f"说话 {sum(n['end'] - n['start'] for n in T['narration']):.1f} 秒")
for w in warns: print('提示：', w)
for e in errs: print('错误：', e)
if '--table' in sys.argv:
    print('\n| 镜头 | 起止（秒） | 帧 | 时长 | 站 | 内容 | 状态 |\n|---|---|---|---|---|---|---|')
    st = {x['id']: x['name'] for x in T['stations']}
    for s in shots:
        print(f"| {s['id']} | {s['start']:.1f}–{s['end']:.1f} | {round(s['start'] * fps) + 1}–{round(s['end'] * fps)} | {s['end'] - s['start']:.0f} | {st.get(s['station'], '—')} | {s['name']} | {s['status']} |")
sys.exit(1 if errs else 0)
