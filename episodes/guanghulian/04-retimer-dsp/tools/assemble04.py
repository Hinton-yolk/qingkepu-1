# 用 04 正片的剪纸条头部 + 03 旁白版的时间表工具 / 字幕 / 检查，拼出 04 小红书版的时间表脚本：python3 tools/assemble04.py u|d
import sys
v = sys.argv[1]; OUT = f'desk_{v}.json'; FIRST = {'u': 'u1', 'd': 'd1'}[v]
a = open('build_desk.py', encoding='utf-8').read().split('\n'); b = open('build_desk_voice.py', encoding='utf-8').read().split('\n')
i_e9 = [i for i, l in enumerate(a) if l.startswith("strip('E9'")][0]; i_pl = [i for i, l in enumerate(a) if l.startswith('# ---------- 摆放')][0]; i_sz = [i for i, l in enumerate(a) if l.startswith('def SZ')][0]
head = '\n'.join(a[:i_e9 + 1]); helpers = '\n'.join(a[i_pl:i_sz + 1])
head = head.replace('# 白话光互连 04《检修站：模糊的信号怎么修回来？》Vox 竖屏 —— 桌面布局与时间表（唯一的真源）', f'# 白话光互连 04 · 小红书版 {v}（由 tools/assemble04.py 拼出，别直接改这个文件）')
tools_ = '\n'.join(b[125:204]); tail = '\n'.join(b[386:])
tools_ = tools_.replace("配音/script_ep3.json", "配音/script_x.json").replace("配音/align_ep3.json", "配音/align_x.json").replace("f'配音/fish/{lid}.wav'", "f'配音/fish_x/{lid}.wav'")
assert 'fish_x' in tools_
tail = tail.replace("if cid != 'H0' and abs(", "if abs(").replace("FORCE = {}", f"FORCE = {{('{FIRST}', 0): (False, '第一帧：大字问题已经贴在实物上')}}")
tail = tail.replace("LENS_TXT = '方方正正的台阶棱角被削掉跳变变得迟缓'", "LENS_TXT = '收到的波形一连串时刻的高低记成数字'")
tail = tail.replace("station=[[2, HUD_IN + 1.5]], hudIn=HUD_IN", "station=[[2, HUD_IN + 1.5]], stn=['打包出发', '路上', '中转', '干线', '签收'], rev=REV, hudIn=HUD_IN").replace("'代码工程/ep3/desk_voice.json'", f"'代码工程/ep4/{OUT}'")
assert 'stn=' in tail and OUT in tail
open(f'build_desk_{v}.py', 'w', encoding='utf-8').write('\n'.join([head, helpers, open(f'places_{v}.py', encoding='utf-8').read(), tools_, open(f'timeline_{v}.py', encoding='utf-8').read(), tail]) + '\n')
print(f'build_desk_{v}.py')
