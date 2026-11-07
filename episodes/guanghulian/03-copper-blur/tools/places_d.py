# ---------- 下集的摆放 ----------
def bare(cid): CARDS[cid]['bare'] = True
place_card('RK', 'rack', L, 1000, 1300, 0.0); bare('RK'); COLY[L] += 350
LAST[0] = 0
place_card('RT', 'route', R, 900, 700, 0.008)
place_card('H0', 'blur', L, 900, 760, -0.008)
place_stack('fix', ['X0', 'X1', 'X2', 'X3', 'X4', 'X4b'], R); place_card('K8', 'fixes', L, 900, 1000, 0.008)
place_stack('fix3', ['X5', 'X6', 'X7', 'X8', 'X9', 'X10'], R); place_card('C2', 'cables', L, 1000, 1180, 0.0); bare('C2'); place_card('K9', 'repair', R, 900, 900, -0.008)
place_stack('copper', ['Y1', 'Y2', 'Y3', 'Y4', 'Y5'], L); place_card('RK2', 'rack', R, 1000, 1300, 0.0); bare('RK2'); place_card('K10', 'split', L, 900, 760, 0.01)
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E9'], 850)
place_card('HE', 'here', 850, 1000, 260, 0.0); bare('HE')
for _cid in [c for c in CLIPS if c not in STACK_OF]: del CLIPS[_cid]          # 这一集用不到的纸条不上桌
