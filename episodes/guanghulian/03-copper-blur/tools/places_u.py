# ---------- 上集的摆放：按出场顺序左右两列交替 ----------
def bare(cid): CARDS[cid]['bare'] = True
place_card('C0', 'cables', L, 1000, 1180, 0.0); bare('C0'); COLY[L] += 350        # 第一帧下面别露出下一张卡片
LAST[0] = 0
place_card('RT', 'route', R, 900, 700, 0.008)
place_card('H0', 'blur', L, 900, 760, -0.008)
place_stack('ideal', ['W1', 'W2', 'W3', 'W4'], R); place_stack('weak', ['A1', 'A2', 'A3', 'A4', 'A5'], R)
place_card('K1', 'corridor', L, 900, 720, -0.008); place_card('K3', 'weaken', L, 900, 820, 0.008)
place_stack('tail', ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9'], R); place_card('K4', 'tail', L, 900, 1100, 0.008)
place_card('G1', 'glitch', R, 900, 980, -0.01)
place_stack('far', ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'], L); place_card('K6', 'faster', R, 900, 960, 0.01)
place_stack('reach', ['R1', 'R2', 'R3'], L); place_card('C1', 'cables', R, 1000, 1180, 0.0); bare('C1'); place_card('K7', 'reach', L, 900, 600, -0.01)
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E9'], 850)
place_card('HE', 'here', 850, 1000, 260, 0.0); bare('HE')
for _cid in [c for c in CLIPS if c not in STACK_OF]: del CLIPS[_cid]          # 这一集用不到的纸条不上桌
