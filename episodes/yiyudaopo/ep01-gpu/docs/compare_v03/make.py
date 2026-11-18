# v02 ↔ v03 对比图：python3 docs/compare_v03/make.py（在 ep01-gpu 目录下运行）
import os, subprocess
from PIL import Image, ImageDraw, ImageFont
V2, V3 = 'remotion/out/EP01_Pilot_v02.mp4', 'remotion/out/EP01_Pilot_v03.mp4'
TMP = '/tmp/claude-0/-home-user-kepu-studio/29e17a9d-e119-5534-8238-01fc32566c1d/scratchpad'
font = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 34)
def grab(v, t):
    out = f'{TMP}/cmp3_{os.path.basename(v)}_{t}.png'
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(t), '-i', v, '-frames:v', '1', '-vf', 'scale=360:640', out], check=True); return Image.open(out)
def sheet(name, title, t2, t3):
    n = max(len(t2), len(t3)); S = Image.new('RGB', (n * 370 + 20, 2 * 700 + 70), (24, 24, 28)); D = ImageDraw.Draw(S)
    D.text((20, 14), title, font=font, fill=(255, 230, 150))
    for row, (lab, v, ts) in enumerate([('v02', V2, t2), ('v03', V3, t3)]):
        y = 70 + row * 700; D.text((20, y), lab, font=font, fill=(255, 255, 255))
        for k, t in enumerate(ts):
            S.paste(grab(v, t), (20 + k * 370, y + 50)); D.text((24 + k * 370, y + 52), f'{t}s', font=font, fill=(255, 255, 0))
    S.save(f'docs/compare_v03/{name}.jpg', quality=82)
sheet('01_opening', '开头：v02 标题 + 对话卡 + GPU 标签互相抢；v03 一个焦点、一个问题', [0.5, 2.0, 4.5, 7.0], [0.3, 1.9, 2.9, 3.9])
sheet('02_ai_calc', 'AI 计算：v02 像一页页讲义；v03 同一个舞台里变形、移动', [31.8, 36.9, 41.0, 44.5], [17.6, 20.3, 25.0, 29.5])
sheet('03_cpu_gpu', 'CPU / GPU：v02 两张方格图 + 分支分歧；v03 同一批任务分别交给两边', [55.5, 59.5, 63.5, 67.6], [39.0, 42.0, 46.0, 48.5])
sheet('04_conclusion', '结论：v02 黑底大字 7 秒；v03 计算流进 GPU，旁白说一遍', [71.6, 75.6, 79.8, 96.5], [51.0, 55.0, 66.0, 72.5])
print('ok')
