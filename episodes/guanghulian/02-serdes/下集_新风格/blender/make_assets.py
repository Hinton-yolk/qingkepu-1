# 生成草稿用的贴图：主持人纸片立牌（白纸边）、手机聊天界面（正常 / 乱码）、比特串（高低电平）
import os, sys, random, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, 'assets'); os.makedirs(A, exist_ok=True)
CUT = sys.argv[1]                                   # 抠好图的目录（A.png、B.png 等）
for k in ('A', 'B'):
    c = Image.open(os.path.join(CUT, k + '.png')).convert('RGBA'); pad = 24
    big = Image.new('RGBA', (c.width + 2 * pad, c.height + 2 * pad)); big.alpha_composite(c, (pad, pad))
    al = big.split()[3].filter(ImageFilter.MaxFilter(41)).filter(ImageFilter.GaussianBlur(1.2))
    paper = Image.new('RGBA', big.size, (247, 243, 233, 255)); paper.putalpha(al); paper.alpha_composite(big)
    paper.save(os.path.join(A, f'standee_{k}.png')); print('standee', k, paper.size)
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
def chat(path, msg):
    """只放一条大消息：手机尺寸下也认得出字（审核：字至少 60 px / 1080 宽）"""
    W, H = 720, 1560; im = Image.new('RGB', (W, H), (16, 17, 20)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 92); fs = ImageFont.truetype(FONT, 40)
    d.rectangle([0, 0, W, 170], fill=(28, 29, 33)); d.text((W // 2, 110), '阿杰', font=fs, fill=(230, 230, 230), anchor='mm')
    d.rounded_rectangle([40, 300, 560, 430], 30, fill=(44, 46, 52)); d.text((80, 365), '晚上有空吗？', font=ImageFont.truetype(FONT, 60), fill=(225, 225, 225), anchor='lm')
    lines = [msg[:5], msg[5:]]
    d.rounded_rectangle([90, 520, W - 30, 800], 34, fill=(76, 186, 96))
    for k, ln in enumerate(lines): d.text((125, 595 + k * 120), ln, font=f, fill=(12, 20, 12), anchor='lm')
    im.save(path)
chat(os.path.join(A, 'screen_ok.png'), '今晚七点，老地方见')
chat(os.path.join(A, 'screen_bad.png'), '今晚□◆※＃％＆＠◇')       # 少了一位以后，后面整串错位成乱码
NB = 120
def bits_png(name, bits, blur=0):
    row = np.array([[255 if b else 30 for b in bits for _ in range(16)]], np.uint8)
    im = Image.fromarray(np.repeat(row, 8, 0), 'L')
    if blur: im = im.filter(ImageFilter.BoxBlur(blur)).filter(ImageFilter.GaussianBlur(blur))
    im.save(os.path.join(A, name)); return bits
random.seed(7)
BITS = [1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0] * 4   # 第 2–6 位是连续五个 1
LONG = [1, 0, 0, 1] + [1] * 26 + [0, 1] * 45                                                            # 一长串 1（y7）
bits_png('bits.png', BITS); bits_png('bits_long.png', LONG[:NB]); bits_png('bits_blur.png', BITS, blur=5)
import json; json.dump({'normal': BITS, 'long': LONG[:NB], 'blur': BITS}, open(os.path.join(A, 'bits.json'), 'w'))
print('bits', len(BITS), len(LONG[:NB]))
