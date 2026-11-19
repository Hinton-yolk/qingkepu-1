# 运动测试的 2D 层：每帧叠字幕（两句之间交叉淡入淡出）、小字、标签条（按锚点跟着物体走），加细颗粒。
# 用法：python3 motion_overlay.py <3D 帧目录> <输出目录> [fps]
import sys, os, json, glob
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from overlay import f, NOTO, NOTO_R, INK, YEL, grain, chip

def seg(t, a, b): return max(0.0, min(1.0, (t - a) / (b - a)))

CAP2 = [[('每写一个字，', 'w')], [('都要把模型', 'w'), ('从头到尾', 'y'), ('过一遍', 'w')]]
CAP3 = [[('这里选了「', 'w'), ('海', 'y'), ('」，', 'w')], [('后面是「边看日落」', 'w')]]
NOTE2, NOTE3 = '模型的层数、格子数为示意', '示意：前一个字不同，后面整句都不同'

def caption(im, caps, note, alpha):
    if alpha <= 0: return im
    layer = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    fc = f(NOTO, 60); lh = 80; cy = 1480
    widths = [sum(d.textlength(s, font=fc) for s, _ in line) for line in caps]
    bw = max(widths) + 80; bh = lh * len(caps) + 40
    d.rounded_rectangle((540 - bw / 2, cy - bh / 2, 540 + bw / 2, cy + bh / 2), 26, fill=(20, 24, 48, 200))
    for i, line in enumerate(caps):
        x = 540 - widths[i] / 2; y = cy - (len(caps) - 1) * lh / 2 + i * lh
        for s, c in line:
            d.text((x, y), s, font=fc, fill=YEL + (255,) if c == 'y' else (255, 255, 255, 255), anchor='lm'); x += d.textlength(s, font=fc)
    fn = f(NOTO_R, 32); nw = d.textlength(note, font=fn); ny = cy - bh / 2 - 44
    d.rounded_rectangle((540 - nw / 2 - 22, ny - 26, 540 + nw / 2 + 22, ny + 26), 18, fill=(20, 24, 48, 150))
    d.text((540, ny), note, font=fn, fill=(222, 226, 245, 255), anchor='mm')
    a = layer.split()[3].point(lambda v: int(v * alpha)); layer.putalpha(a)
    im.paste(layer, (0, 0), layer); return im

def chip_a(im, cx, cy, text, fill, color, alpha):
    if alpha <= 0: return im
    tmp = im.copy(); chip(tmp, cx, cy, text, fill, color)
    return Image.blend(im, tmp, alpha)

def main(src, dst, fps=30):
    os.makedirs(dst, exist_ok=True)
    for p in sorted(glob.glob(os.path.join(src, 'f*.png'))):
        fi = int(os.path.basename(p)[1:5]); t = fi / fps
        im = grain(Image.open(p).convert('RGB').resize((1080, 1920), Image.LANCZOS), 5.0, seed=fi)
        A = json.load(open(p[:-4] + '.json')); P = {k: (v[0] * 1080, (1 - v[1]) * 1920) for k, v in A.items()}
        im = chip_a(im, P['model'][0], P['model'][1], '模型：一层一层', (75, 63, 140), (255, 255, 255), 1 - seg(t, 0.7, 1.0))
        im = chip_a(im, P['q'][0], P['q'][1], '下一个字', (255, 196, 40), INK, 1 - seg(t, 1.2, 1.4))
        # 换章节时字幕先淡出、再淡入，不叠在一起（叠着读不清）
        im = caption(im, CAP2, NOTE2, 1 - seg(t, 1.5, 1.65))
        im = caption(im, CAP3, NOTE3, seg(t, 1.8, 1.95))
        im.save(os.path.join(dst, os.path.basename(p)))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 30)
