# 主要对象的运动轨迹（世界坐标，不受相机运动影响）：上图俯视（x–y），下图侧视（x–z）；点间隔 0.5 秒
import sys, os, json
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'style3d'))
from overlay import f, NOTO
COLS = [(220, 138, 58), (31, 154, 142), (70, 74, 82), (180, 100, 40), (60, 130, 200), (150, 90, 160), (110, 150, 60), (200, 70, 70), (90, 90, 170), (160, 140, 50), (40, 160, 120), (120, 120, 120)]
def plot(js, out, title):
    D = json.load(open(js)); names = list(D.keys())
    pts = [p['world'] for k in names for p in D[k] if p['world'][2] > -1]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; zs = [p[2] for p in pts]
    W, H = 1400, 1500; im = Image.new('RGB', (W, H), (250, 247, 241)); d = ImageDraw.Draw(im)
    d.text((40, 30), title, font=f(NOTO, 36), fill=(40, 40, 40))
    d.text((40, 80), '世界坐标（不含相机运动）。上：俯视 x–y（下方 = 靠近镜头）；下：侧视 x–z。点间隔 0.5 秒，箭头 = 终点', font=f(NOTO, 22), fill=(90, 90, 90))
    x0, x1 = min(xs) - 0.5, max(xs) + 0.5
    for (panel, (ya, yb), (top, bot), vals) in (('俯视', (min(ys) - 0.5, max(ys) + 0.5), (140, 780), 1), ('侧视', (min(zs) - 0.2, max(zs) + 0.4), (840, 1460), 2)):
        d.rectangle((40, top, W - 40, bot), outline=(200, 195, 185), width=2); d.text((52, top + 8), panel, font=f(NOTO, 24), fill=(120, 120, 120))
        def P(x, v): return (60 + (x - x0) / (x1 - x0) * (W - 120), bot - 20 - (v - ya) / (yb - ya) * (bot - top - 60))
        for i, k in enumerate(names):
            ps = [P(p['world'][0], p['world'][vals]) for p in D[k] if p['world'][2] > -1]
            if len(ps) < 2 or max(abs(a[0] - ps[0][0]) + abs(a[1] - ps[0][1]) for a in ps) < 3: continue
            c = COLS[i % len(COLS)]; d.line(ps, fill=c, width=4)
            for j in range(0, len(ps), 15): d.ellipse((ps[j][0] - 4, ps[j][1] - 4, ps[j][0] + 4, ps[j][1] + 4), fill=c)
            e = ps[-1]; d.ellipse((e[0] - 8, e[1] - 8, e[0] + 8, e[1] + 8), outline=c, width=3)
            d.text((e[0] + 10, e[1] - 12 - 0 * i), k.replace('✕', '叉号'), font=f(NOTO, 22), fill=c)
    im.save(out, quality=90)
if __name__ == '__main__':
    for s, name, d in (('a', 'AnimationTest_A_Branch', 'out/post'), ('b', 'AnimationTest_B_ModelFlow', 'out/post'), ('c', 'AnimationTest_C_SpeculativeDecoding', 'out/post'), ('int', 'EP01_IntegratedAnimation_Test01', 'out/post_int')):
        js = f'{d}/{name}_轨迹.json'
        if os.path.exists(js) and (len(sys.argv) < 2 or s in sys.argv[1:]):
            plot(js, f'{d}/{name}_轨迹.jpg', name + ' · 主要对象的运动轨迹'); print('ok', s)
