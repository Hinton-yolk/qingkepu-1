"""合成用的小部件（接触表和成片共用）：后期（高光晕、暗角、颗粒，参数同 blender_desk_look/post.py）、小纸签、字幕条、五站条、系列名。
画面坐标都按 1080×1920 设计，s = 实际宽度 / 1080。界面避让按系列 skill 的抖音版：字幕 y = 1400，小签放在 170–1320 之间；顶部不放五站条。"""
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

CREAM, DARK, PAPER, CORAL = (241, 233, 214), (29, 29, 28), (238, 231, 214), (214, 84, 62)
STATIONS = ["打包出发", "路上", "中转", "干线", "签收"]


def blur(x, sigma):
    r = int(sigma * 3) | 1
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2); k /= k.sum()
    for ax in (0, 1):
        pad = [(0, 0)] * x.ndim; pad[ax] = (r, r)
        xp = np.pad(x, pad, mode="edge"); out = np.zeros_like(x)
        for i, w in enumerate(k):
            sl = [slice(None)] * x.ndim; sl[ax] = slice(i, i + x.shape[ax])
            out += w * xp[tuple(sl)]
        x = out
    return x


def grade(im, seed=0):
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    H, W, _ = a.shape
    lin = a ** 2.2
    lum = lin @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    hi = np.clip((lum - 0.62) / 0.38, 0, 1)[..., None] * lin
    lin = lin + 0.22 * blur(hi, W * 0.006) * np.array([1.0, 0.42, 0.18], np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r2 = ((xx - W / 2) / (W / 2)) ** 2 * 0.55 + ((yy - H / 2) / (H / 2)) ** 2 * 0.75
    lin *= (1 - 0.14 * np.clip(r2 / 1.3, 0, 1) ** 1.5)[..., None]
    out = np.clip(lin, 0, 1) ** (1 / 2.2)
    g = blur(np.random.default_rng(seed).normal(0, 1, (H, W)).astype(np.float32), 0.6); g /= g.std()
    l2 = out @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    out += (0.012 * g * (0.35 + 1.3 * l2 * (1 - l2) * 2))[..., None]
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).convert("RGBA")


class Kit:
    def __init__(self, fonts, W):
        self.s = s = W / 1080; self.W = W; self.H = int(W * 16 / 9)
        B = f"{fonts}/NotoSansSC-Bold.otf"
        self.f_tag = ImageFont.truetype(B, int(50 * s)); self.f_big = ImageFont.truetype(B, int(78 * s))
        self.f_sub = ImageFont.truetype(B, int(54 * s)); self.f_st = ImageFont.truetype(B, int(34 * s))
        self.f_note = ImageFont.truetype(B, int(30 * s)); self.f_ser = ImageFont.truetype(B, int(30 * s))

    def _torn(self, ld, box, fill, seed):
        """深色撕边条：左右两边是不齐的。"""
        x0, y0, x1, y1 = box; r = random.Random(seed); n = 7; j = 7 * self.s
        left = [(x0 + r.uniform(-j, j), y0 + (y1 - y0) * i / n) for i in range(n + 1)]
        right = [(x1 + r.uniform(-j, j), y1 - (y1 - y0) * i / n) for i in range(n + 1)]
        ld.polygon(left[::-1][::-1] + right, fill=fill)

    def tag(self, im, xy, text, alpha=1.0, anchor="lt", big=False, line_to=None):
        """小纸签：米色底、深色字。xy 是 anchor 指的那个角 / 边中点（l m r + t m b）。line_to：从签引一根细线到这个点。"""
        if alpha <= 0: return
        s = self.s; font = self.f_big if big else self.f_tag
        d = ImageDraw.Draw(im); b = d.textbbox((0, 0), text, font=font)
        pad = int((16 if big else 11) * s)
        w, h = b[2] - b[0] + 2 * pad, b[3] - b[1] + 2 * pad
        x, y = xy
        x -= {"l": 0, "m": w / 2, "r": w}[anchor[0]]; y -= {"t": 0, "m": h / 2, "b": h}[anchor[1]]
        x = min(max(x, 24 * s), self.W - w - 24 * s); y = min(max(y, 170 * s), 1325 * s - h)        # 不出画，不进界面避让区
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        if line_to:
            ld.line([line_to, (x + w / 2, y + h / 2)], fill=(*PAPER, int(255 * alpha)), width=max(1, int(3 * s)))
            ld.ellipse([line_to[0] - 5 * s, line_to[1] - 5 * s, line_to[0] + 5 * s, line_to[1] + 5 * s], fill=(*PAPER, int(255 * alpha)))
        ld.rectangle([x + 3 * s, y + 4 * s, x + w + 3 * s, y + h + 4 * s], fill=(0, 0, 0, int(80 * alpha)))
        ld.rectangle([x, y, x + w, y + h], fill=(*PAPER, int(255 * alpha)), outline=(110, 102, 90, int(255 * alpha)))
        ld.text((x + pad - b[0], y + pad - b[1]), text, font=font, fill=(26, 24, 22, int(255 * alpha)))
        im.alpha_composite(lay)

    @staticmethod
    def wrap(text, limit=13):
        """超过 limit 个字就拆成两行：优先在靠中间的标点后面断；没有合适标点的句子在 subs.json 里用「|」标断行处。"""
        if "|" in text: return text.split("|")                                  # subs.json 里用「|」标了断行的位置
        if len(text) <= limit: return [text]
        cuts = [i + 1 for i, ch in enumerate(text[:-1]) if ch in "，、；：,"] or [len(text) // 2]
        k = min(cuts, key=lambda i: abs(i - len(text) / 2))
        if max(k, len(text) - k) > limit + 3: k = len(text) // 2
        return [text[:k], text[k:]]

    def subtitle(self, im, text):
        if not text: return
        s = self.s; d = ImageDraw.Draw(im); lines = self.wrap(text)
        bs = [d.textbbox((0, 0), t, font=self.f_sub) for t in lines]
        lh = int(66 * s); w = max(b[2] - b[0] for b in bs); h = lh * len(lines)
        cx, cy = self.W / 2 - 30 * s, 1400 * s                                   # 略偏左，让开抖音右侧的按钮
        lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        self._torn(ld, (cx - w / 2 - 30 * s, cy - h / 2 - 16 * s, cx + w / 2 + 30 * s, cy + h / 2 + 18 * s), (*DARK, 235), len(text))
        for i, (t, b) in enumerate(zip(lines, bs)):
            ld.text((cx - (b[2] - b[0]) / 2 - b[0], cy - h / 2 + i * lh + (lh - (b[3] - b[1])) / 2 - b[1]), t, font=self.f_sub, fill=(*CREAM, 255))
        im.alpha_composite(lay)

    def chrome(self, im):
        """右上角系列名。顶部五站条在实拍质感的片子里不放（用户 2026-11-11：「实拍质感的不要留顶部的五站条了，大概率大家不会关注，还影响画面」）。"""
        s = self.s; lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        t = "一语道破 · 白话光互连"; b = ld.textbbox((0, 0), t, font=self.f_ser)
        ld.text((self.W - (b[2] - b[0]) - 36 * s, 112 * s), t, font=self.f_ser, fill=(*CREAM, 200), stroke_width=max(1, int(2 * s)), stroke_fill=(20, 20, 20, 160))
        im.alpha_composite(lay)

    def note(self, im, text):
        """角注：左下角，字幕上方。全片只有 y3 一处。"""
        s = self.s; d = ImageDraw.Draw(im)
        d.text((36 * s, 1282 * s), text, font=self.f_note, fill=(*CREAM, 235), stroke_width=max(1, int(3 * s)), stroke_fill=(20, 20, 20, 220))
