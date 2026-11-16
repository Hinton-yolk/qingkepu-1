#!/usr/bin/env python3
"""Subset the two faces to the characters the film uses (scanned from timeline.js + index.html).
Display: Smiley Sans (得意黑, OFL). UI: Noto Sans CJK SC Bold (OFL). Writes assets/fonts/*.woff2."""
import pathlib, re
from fontTools import subset
from fontTools.ttLib import TTFont, TTCollection

ROOT = pathlib.Path(__file__).resolve().parent.parent
text = "".join((ROOT / f).read_text(encoding="utf-8") for f in ["timeline.js", "index.html", "styleframes.html"] if (ROOT / f).exists())
chars = set(ch for ch in text if ord(ch) > 0x7E) | set(chr(c) for c in range(0x20, 0x7F))
chars |= set("，。？！“”：°·—…0123456789")
uni = sorted(ord(c) for c in chars)

def sub(font, out):
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = ["*"]; opts.name_IDs = ["*"]
    s = subset.Subsetter(opts); s.populate(unicodes=uni); s.subset(font)
    font.flavor = "woff2"; font.save(str(out)); print(out.name, out.stat().st_size // 1024, "KB")

sub(TTFont(str(ROOT / "assets/fonts/SmileySans-Oblique.ttf")), ROOT / "assets/fonts/smiley.woff2")
for weight, f in [("bold", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"), ("regular", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")]:
    col = TTCollection(f)
    sc = next(ft for ft in col.fonts if "CJK SC" in ft["name"].getDebugName(1))
    sub(sc, ROOT / f"assets/fonts/noto-sc-{weight}.woff2")
print(len(uni), "code points")
