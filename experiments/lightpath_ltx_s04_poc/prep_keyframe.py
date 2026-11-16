"""GPT keyframe (any 9:16 size) -> 1088x1920 LTX keyframe: scale to height 1920, edge-replicate to 1088 wide.
   python3 prep_keyframe.py <gpt image> <out png> [<clay png to check alignment against>]"""
import sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGB')
w = round(im.width * 1920 / im.height)
im = im.resize((w, 1920), Image.LANCZOS)
if w >= 1088:
    l = (w - 1088) // 2
    canvas = im.crop((l, 0, l + 1088, 1920))
else:
    canvas = Image.new('RGB', (1088, 1920))
    l = (1088 - w) // 2
    canvas.paste(im, (l, 0))
    for x in range(l):
        canvas.paste(im.crop((0, 0, 1, 1920)), (x, 0))
    for x in range(l + w, 1088):
        canvas.paste(im.crop((w - 1, 0, w, 1920)), (x, 0))
canvas.save(out)
if len(sys.argv) > 3:
    Image.blend(canvas, Image.open(sys.argv[3]).convert('RGB'), 0.5).resize((544, 960)).save(out.replace('.png', '_overlay.jpg'))
print(out, canvas.size)
