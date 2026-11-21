#!/usr/bin/env python3
"""Subset Noto Sans CJK SC (OFL) Bold/Regular to the characters used in timeline.js + index.html -> assets/fonts/*.woff2."""
import pathlib
from fontTools import subset
from fontTools.ttLib import TTCollection
ROOT = pathlib.Path(__file__).resolve().parent.parent
text = "".join((ROOT / f).read_text(encoding="utf-8") for f in ["timeline.js", "index.html"])
chars = set(ch for ch in text if ord(ch) > 0x7E) | set(chr(c) for c in range(0x20, 0x7F)) | set("，。？！「」：·…")
uni = sorted(ord(c) for c in chars)
for weight, f in [("bold", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"), ("regular", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")]:
    sc = next(ft for ft in TTCollection(f).fonts if "CJK SC" in ft["name"].getDebugName(1))
    o = subset.Options(); o.flavor = "woff2"; o.layout_features = ["*"]
    s = subset.Subsetter(o); s.populate(unicodes=uni); s.subset(sc); sc.flavor = "woff2"
    out = ROOT / f"assets/fonts/noto-sc-{weight}.woff2"; sc.save(str(out)); print(out.name, out.stat().st_size // 1024, "KB")
