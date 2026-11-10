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
    W, H = 720, 1560; im = Image.new('RGB', (W, H), (16, 17, 20)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 44); fs = ImageFont.truetype(FONT, 30)
    d.rectangle([0, 0, W, 150], fill=(28, 29, 33)); d.text((W // 2, 100), '阿杰', font=fs, fill=(230, 230, 230), anchor='mm')
    d.rounded_rectangle([40, 260, 470, 350], 22, fill=(44, 46, 52)); d.text((70, 305), '晚上有空吗？', font=f, fill=(225, 225, 225), anchor='lm')
    tw = d.textlength(msg, font=f); d.rounded_rectangle([W - 70 - tw - 60, 420, W - 40, 510], 22, fill=(76, 186, 96))
    d.text((W - 70 - tw - 30, 465), msg, font=f, fill=(12, 20, 12), anchor='lm')
    im.save(path)
chat(os.path.join(A, 'screen_ok.png'), '今晚七点，老地方见')
chat(os.path.join(A, 'screen_bad.png'), '仒晩亼祘，耂坔方见')
random.seed(7); bits = [1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0] * 4
row = np.array([[255 if b else 40 for b in bits for _ in range(16)]], np.uint8)
Image.fromarray(np.repeat(row, 8, 0), 'L').save(os.path.join(A, 'bits.png')); print('bits', len(bits))
