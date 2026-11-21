#!/usr/bin/env python3
"""Subset Noto Sans SC (500/700/900) to the characters this episode uses (scanned from timeline.js + index.html).
Source: the full GB2312 instances in templates/guanghulian/engine/lib/fonts/ (OFL). Writes assets/fonts/NotoSansSC-*.woff.
Characters outside GB2312 (e.g. 龘) fall back to the system Noto Sans CJK SC at render time."""
import pathlib
from fontTools import subset
from fontTools.ttLib import TTFont
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT.parents[2] / "templates/guanghulian/engine/lib/fonts"
text = "".join((ROOT / f).read_text(encoding="utf-8") for f in ["timeline.js", "index.html"])
chars = set(ch for ch in text if ord(ch) > 0x7E) | set(chr(c) for c in range(0x20, 0x7F)) | set("，。？！“”：·—…≈×≠✓")
for w in (500, 700, 900):
    f = TTFont(str(SRC / f"NotoSansSC-{w}.woff"))
    o = subset.Options(); o.flavor = "woff"; o.layout_features = ["*"]; o.name_IDs = ["*"]
    s = subset.Subsetter(o); s.populate(unicodes=[ord(c) for c in chars]); s.subset(f)
    out = ROOT / f"assets/fonts/NotoSansSC-{w}.woff"; f.flavor = "woff"; f.save(str(out)); print(out.name, out.stat().st_size // 1024, "KB")
