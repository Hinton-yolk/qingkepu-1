# 生成 V02 手机界面贴图：用户输入改为「续写这句话：周末我想……」（其余和 V01 的 ui_phone.png 一样）
import os
from PIL import Image, ImageDraw, ImageFont
H = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(H, '..', 'style3d', 'out', 'motion_v2', 'NotoSansSC-Bold.otf')
im = Image.open(os.path.join(H, 'ui_phone.png')).convert('RGB'); d = ImageDraw.Draw(im)
d.rectangle((60, 260, 1000, 420), fill=im.getpixel((20, 300)))                # 擦掉旧的用户气泡
ft = ImageFont.truetype(FONT, 54); txt = '续写这句话：周末我想……'
w = d.textlength(txt, font=ft); x1 = 940; x0 = x1 - w - 90
d.rounded_rectangle((x0, 280, x1, 400), 60, fill=(213, 228, 222))
d.text(((x0 + x1) / 2, 340), txt, font=ft, fill=(36, 98, 84), anchor='mm')
im.save(os.path.join(H, 'ui_phone_v2.png'))
