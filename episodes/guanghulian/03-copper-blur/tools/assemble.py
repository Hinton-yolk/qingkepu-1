# 用 build_desk_voice.py 的框架拼出各版时间表脚本：python3 tools/assemble.py u|d|x
# 头部（剪纸条）、时间表工具、字幕和检查沿用旧版；摆放 places_<v>.py 和时间表 timeline_<v>.py 每版各写一份。
import sys
v = sys.argv[1]; OUT = f'desk_{v}.json'; FIRST = {'x': 'X1', 'u': 'X1', 'd': 'D1', 't': 'X1', 's': 'D1'}[v]; DOUYIN = v in ('t', 's')   # t、s = 抖音版两条
src = open('build_desk_voice.py', encoding='utf-8').read().split('\n')
head = '\n'.join(src[0:70]); mid1 = '\n'.join(src[70:110]); tools_ = '\n'.join(src[125:204]); tail = '\n'.join(src[386:])
head = head.replace('# 白话光互连 03 · 旁白版（竖屏，抖音/小红书）', f'# 白话光互连 03 · 小红书改版 {v}（由 tools/assemble.py 拼出，别直接改这个文件）').replace('→ 代码工程/ep3/desk_voice.json', f'→ 代码工程/ep3/{OUT}')
tools_ = tools_.replace("配音/script_ep3.json", "配音/script_x.json").replace("配音/align_ep3.json", "配音/align_x.json").replace("f'配音/fish/{lid}.wav'", "f'配音/fish_x/{lid}.wav'")
tail = tail.replace("if cid != 'H0' and abs(", "if abs(").replace("FORCE = {}", f"FORCE = {{('{FIRST}', 0): (False, '第一帧：大字问题已经贴在实物上')}}")
if DOUYIN:   # 抖音界面避让：字幕提到 1400、导航条挪到 200；纸条和卡片放在 310–1320 之间
    tools_ = tools_.replace("def fitstack(name, top=235, bot=1440):", "def fitstack(name, top=310, bot=1320):")
    tools_ = tools_.replace("h = CARDS[cid]['h']; z = min(z, 1205 / h); dy = max(0, h / 2 - 470 / z)\n    if 960 - (h / 2 + dy) * z < 215: dy = (960 - 215) / z - h / 2", "h = CARDS[cid]['h']; z = min(z, 1010 / h); dy = 145 / z")
    assert 'dy = 145 / z' in tools_ and 'top=310' in tools_
    tail = tail.replace("assert not (1470 < sy < 1660)", "assert not (1310 < sy < 1500)").replace("200 < sy < 1860", "300 < sy < 1860")
tail = tail.replace("station=[[2, HUD_IN + 1.5]], hudIn=HUD_IN", "station=[[2, HUD_IN + 1.5]], stn=['打包出发', '路上', '中转', '干线', '签收'], rev=REV, hudIn=HUD_IN").replace("'代码工程/ep3/desk_voice.json'", f"'代码工程/ep3/{OUT}'")
if DOUYIN: tail = tail.replace("rev=REV, hudIn=HUD_IN", "rev=REV, subY=1400, hudY=200, hudIn=HUD_IN"); assert "subY=1400" in tail
place = "\nDROP = {'T1', 'T2', 'I1', 'I2', 'I3', 'I4', 'M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'W0'}\nS = [x for x in S if x[0] not in DROP]"
open(f'build_desk_{v}.py', 'w', encoding='utf-8').write('\n'.join([head, place, mid1, open(f'places_{v}.py', encoding='utf-8').read(), tools_, open(f'timeline_{v}.py', encoding='utf-8').read(), tail]) + '\n')
print('build_desk_%s.py' % v, '（抖音）' if DOUYIN else '')
