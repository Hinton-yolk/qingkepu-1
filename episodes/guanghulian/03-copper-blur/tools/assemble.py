# 用 build_desk_voice.py 的框架拼出各版时间表脚本：python3 tools/assemble.py u|d|x
# 头部（剪纸条）、时间表工具、字幕和检查沿用旧版；摆放 places_<v>.py 和时间表 timeline_<v>.py 每版各写一份。
import sys
v = sys.argv[1]; OUT = {'x': 'desk_x.json', 'u': 'desk_u.json', 'd': 'desk_d.json'}[v]; FIRST = {'x': 'X1', 'u': 'X1', 'd': 'D1'}[v]
src = open('build_desk_voice.py', encoding='utf-8').read().split('\n')
head = '\n'.join(src[0:70]); mid1 = '\n'.join(src[70:110]); tools_ = '\n'.join(src[125:204]); tail = '\n'.join(src[386:])
head = head.replace('# 白话光互连 03 · 旁白版（竖屏，抖音/小红书）', f'# 白话光互连 03 · 小红书改版 {v}（由 tools/assemble.py 拼出，别直接改这个文件）').replace('→ 代码工程/ep3/desk_voice.json', f'→ 代码工程/ep3/{OUT}')
tools_ = tools_.replace("配音/script_ep3.json", "配音/script_x.json").replace("配音/align_ep3.json", "配音/align_x.json").replace("f'配音/fish/{lid}.wav'", "f'配音/fish_x/{lid}.wav'")
tail = tail.replace("if cid != 'H0' and abs(", "if abs(").replace("FORCE = {}", f"FORCE = {{('{FIRST}', 0): (False, '第一帧：大字问题已经贴在实物上')}}")
tail = tail.replace("station=[[2, HUD_IN + 1.5]], hudIn=HUD_IN", "station=[[2, HUD_IN + 1.5]], stn=['打包出发', '路上', '中转', '干线', '签收'], rev=REV, hudIn=HUD_IN").replace("'代码工程/ep3/desk_voice.json'", f"'代码工程/ep3/{OUT}'")
place = "\nDROP = {'T1', 'T2', 'I1', 'I2', 'I3', 'I4', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'W0'}\nS = [x for x in S if x[0] not in DROP]"
open(f'build_desk_{v}.py', 'w', encoding='utf-8').write('\n'.join([head, place, mid1, open(f'places_{v}.py', encoding='utf-8').read(), tools_, open(f'timeline_{v}.py', encoding='utf-8').read(), tail]) + '\n')
print('build_desk_%s.py' % v)
