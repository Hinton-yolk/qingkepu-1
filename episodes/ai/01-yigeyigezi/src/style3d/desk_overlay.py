# 美术规范样张的 2D 层：字幕条石墨灰、关键词琥珀橙、小字、细颗粒（颜色克制）
import sys, os
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overlay import f, NOTO, NOTO_R, SMILEY, grain
from film_overlay import CAPS, parse, wrap_note
AMB = (232, 144, 44); GR = (38, 40, 45); INK2 = (40, 42, 47)

def caption(im, b):
    text, note, analog = CAPS[b]
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    fc = f(NOTO, 60); lh = 80; cy = 1480
    lines = [parse(l) for l in text.split('/')]
    widths = [sum(d.textlength(s, font=fc) for s, _ in l) for l in lines]
    bw = max(widths) + 80; bh = lh * len(lines) + 40
    d.rounded_rectangle((540 - bw / 2, cy - bh / 2, 540 + bw / 2, cy + bh / 2), 22, fill=GR + (215,))
    for i, l in enumerate(lines):
        x = 540 - widths[i] / 2; y = cy - (len(lines) - 1) * lh / 2 + i * lh
        for s, c in l:
            d.text((x, y), s, font=fc, fill=AMB + (255,) if c else (246, 242, 236, 255), anchor='lm'); x += d.textlength(s, font=fc)
    if note:
        fn = f(NOTO_R, 30); nl = wrap_note(d, note, fn)
        nh = 42 * len(nl) + 14; ny1 = cy - bh / 2 - 16; ny0 = ny1 - nh
        nw = max(d.textlength(t, font=fn) for t in nl)
        d.rounded_rectangle((540 - nw / 2 - 22, ny0, 540 + nw / 2 + 22, ny1), 16, fill=GR + (150,))
        for i, t in enumerate(nl): d.text((540, ny0 + 7 + 21 + i * 42), t, font=fn, fill=(232, 228, 220, 255), anchor='mm')
    im.paste(layer, (0, 0), layer)

def title(im):
    d = ImageDraw.Draw(im); l1, l2 = 'AI 为什么', '一个字一个字往外蹦？'
    size = 128
    while d.textlength(l2, font=f(SMILEY, size)) > 800: size -= 2
    ft = f(SMILEY, size); w2 = d.textlength(l2, font=ft); x0 = 540 - w2 / 2; kw = d.textlength('一个字一个字', font=ft)
    d.rectangle((x0 - 4, 383, x0 + kw + 4, 395), fill=AMB)        # 关键词下面一道琥珀色细线（不用大色块）
    d.text((540, 225), l1, font=ft, fill=INK2, anchor='mm'); d.text((540, 340), l2, font=ft, fill=INK2, anchor='mm')

if __name__ == '__main__':
    src, out, shot = sys.argv[1], sys.argv[2], int(sys.argv[3])
    b = {1: 1, 2: 6, 3: 25}[shot]
    im = grain(Image.open(src).convert('RGB').resize((1080, 1920), Image.LANCZOS), 4.0)
    if shot == 1: title(im)
    caption(im, b); im.save(out)
