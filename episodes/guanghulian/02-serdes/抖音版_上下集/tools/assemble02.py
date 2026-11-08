# 02 抖音版（小红书纸桌讲解风格）：用 02 正片的剪纸条头部 + 旁白版的时间表工具 / 字幕 / 检查，拼出时间表脚本：python3 tools/assemble02.py u|d
# 抖音界面避让（同 03 抖音纸桌版）：字幕提到 1400、五站条挪到 200；纸条和卡片放在 310–1320 之间。亮第一站「打包出发」。
import sys
v = sys.argv[1]; OUT = f'desk_{v}.json'; FIRST = {'u': 'x1', 'd': 'y1'}[v]
a = open('build_desk.py', encoding='utf-8').read().split('\n'); b = open('build_desk_voice.py', encoding='utf-8').read().split('\n')
i_e9 = [i for i, l in enumerate(a) if l.startswith("strip('E9'")][0]; i_pl = [i for i, l in enumerate(a) if l.startswith('# ---------- 摆放')][0]; i_sz = [i for i, l in enumerate(a) if l.startswith('def SZ')][0]
head = '\n'.join(a[:i_e9 + 1])
h4 = open('build_desk04_helpers.py', encoding='utf-8').read().split('\n')   # 摆放工具用 04 的（多了 STACK_OF 等）
j_pl = [i for i, l in enumerate(h4) if l.startswith('# ---------- 摆放')][0]; j_sz = [i for i, l in enumerate(h4) if l.startswith('def SZ')][0]; helpers = '\n'.join(h4[j_pl:j_sz + 1])
head = f'# 白话光互连 02 · 抖音版 {v}（由 tools/assemble02.py 拼出，别直接改这个文件）\n' + head
tools_ = '\n'.join(b[125:204]); tail = '\n'.join(b[386:])
tools_ = tools_.replace("配音/script_ep3.json", "配音/script_x.json").replace("配音/align_ep3.json", "配音/align_x.json").replace("f'配音/fish/{lid}.wav'", "f'配音/fish_x/{lid}.wav'")
assert 'fish_x' in tools_
tools_ = tools_.replace("def fitstack(name, top=235, bot=1440):", "def fitstack(name, top=310, bot=1320):")
tools_ = tools_.replace("h = CARDS[cid]['h']; z = min(z, 1205 / h); dy = max(0, h / 2 - 470 / z)\n    if 960 - (h / 2 + dy) * z < 215: dy = (960 - 215) / z - h / 2", "h = CARDS[cid]['h']; z = min(z, 1010 / h); dy = 145 / z")
assert 'dy = 145 / z' in tools_ and 'top=310' in tools_
tail = tail.replace("assert not (1470 < sy < 1660)", "assert not (1310 < sy < 1500)").replace("200 < sy < 1860", "300 < sy < 1860")
tail = tail.replace("if cid != 'H0' and abs(", "if abs(").replace("FORCE = {}", f"FORCE = {{('{FIRST}', 0): (False, '第一帧：大字问题已经贴在实物上')}}")
tail = tail.replace("LENS_TXT = '方方正正的台阶棱角被削掉跳变变得迟缓'", "LENS_TXT = ''")
tail = tail.replace("station=[[2, HUD_IN + 1.5]], hudIn=HUD_IN", "station=[[1, HUD_IN + 1.5]], stn=['打包出发', '路上', '中转', '干线', '签收'], si=0, rev=REV, subY=1400, hudY=200, hudIn=HUD_IN").replace("'代码工程/ep3/desk_voice.json'", f"'代码工程/ep2x/{OUT}'")
assert 'si=0' in tail and OUT in tail
open(f'build_desk_{v}.py', 'w', encoding='utf-8').write('\n'.join([head, helpers, open(f'places_{v}.py', encoding='utf-8').read(), tools_, open(f'timeline_{v}.py', encoding='utf-8').read(), tail]) + '\n')
print(f'build_desk_{v}.py（抖音）')
