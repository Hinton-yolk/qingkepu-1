# ---------- 下集的摆放 ----------
def bare(cid): CARDS[cid]['bare'] = True
place_card('RK', 'rack', L, 1000, 1300, 0.0); bare('RK'); COLY[L] += 350
LAST[0] = 0
place_card('RT', 'route', R, 900, 700, 0.008)
place_card('H0', 'blur', L, 900, 760, -0.008)
place_stack('fix', ['X0', 'X1', 'X2', 'X3', 'X4', 'X4b'], R); place_card('K8', 'fixes', L, 900, 1000, 0.008)
place_stack('fix3', ['X5', 'X6', 'X7', 'X8', 'X9', 'X10'], R); place_card('C2', 'cables', L, 1000, 1180, 0.0); bare('C2'); place_card('K9', 'repair', R, 900, 900, -0.008)
# 「短距离」在原文 PDF 里跨了行（「……这样的短 / 距离里……」）：Y3 剪到「的」为止，把「短」字从原文剪下来接到 Y4 前面，读起来不断开
strip('Y3s', 2, '在机柜内这样的'); strip('Y4s', 2, '距离里依然大量使用。')     # 新的 id：上集也会剪 Y3/Y4，同名会互相覆盖图片
def prepend_char(cid, page, src_phrase, ch):
    g = [x for x in runs(page, src_phrase)[0] if x[0] == ch][0]; c = CLIPS[cid]; path = os.path.join(ROOT, '代码工程', c['src']); im = Image.open(path).convert('RGB')
    r0 = runs(c['page'], c['text'])[0][0]; base = r0[3]; x0, y0, x1, y1 = c['crop']; m = r0[1] - x0 - 0.6
    gx0, gx1 = g[1] - 0.6, g[2] + 0.6; wg = gx1 - gx0
    gim = page_img(page).crop((round(gx0 * DPI), round((g[3] - (base - y0)) * DPI), round(gx1 * DPI), round((g[3] - (base - y0)) * DPI) + im.height))
    out = Image.new('RGB', (im.width + gim.width, im.height), 'white'); k = round(m * DPI)
    out.paste(im.crop((0, 0, k, im.height)), (0, 0)); out.paste(gim, (k, 0)); out.paste(im.crop((k, 0, im.width, im.height)), (k + gim.width, 0)); out.save(path, optimize=True)
    c['crop'][0] = round(x0 - gim.width / DPI, 2); c['text'] = ch + c['text']
prepend_char('Y4s', 2, '在机柜内这样的短', '短')
place_stack('copper', ['Y1', 'Y2', 'Y3s', 'Y4s', 'Y5'], L)
for _c in ('Y3', 'Y4'): CLIPS.pop(_c, None); place_card('RK2', 'rack', R, 1000, 1300, 0.0); bare('RK2'); place_card('K10', 'split', L, 900, 760, 0.01)
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E9'], 850)
place_card('HE', 'here', 850, 1000, 260, 0.0); bare('HE')
for _cid in [c for c in CLIPS if c not in STACK_OF]: del CLIPS[_cid]          # 这一集用不到的纸条不上桌
