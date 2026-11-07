# ---------- 抖音第 1 条的摆放 ----------
def bare(cid): CARDS[cid]['bare'] = True
place_card('C0', 'cables', L, 1000, 1180, 0.0); bare('C0'); COLY[L] += 350
LAST[0] = 0
place_card('RT', 'route', R, 900, 700, 0.008)
place_stack('tail', ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9'], L); place_card('K4', 'tail', R, 900, 1100, 0.008)
place_card('G1', 'glitch', L, 900, 980, -0.01)
place_stack('far', ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'], R); place_card('K6', 'faster', L, 900, 960, 0.01)
place_card('C1', 'cables', R, 1000, 1180, 0.0); bare('C1'); place_card('K7', 'reach', L, 900, 600, -0.01)
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E9'], 850)
place_card('HE', 'here', 850, 1000, 260, 0.0); bare('HE')
for _cid in [c for c in CLIPS if c not in STACK_OF]: del CLIPS[_cid]          # 这一条用不到的纸条不上桌
