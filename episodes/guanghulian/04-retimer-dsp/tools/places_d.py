# ---------- 04 下集的摆放 ----------
def bare(cid): CARDS[cid]['bare'] = True
place_card('M0', 'module', L, 1200, 1100, 0.0); bare('M0'); COLY[L] += 350
LAST[0] = 0
place_card('RT', 'route', R, 900, 700, 0.008)
place_stack('samp', ['S1', 'S2', 'S3', 'S4', 'S5', 'S6'], L); place_card('K5', 'dspcalc', R, 900, 1050, 0.008)
place_card('NT', 'note', L, 900, 700, -0.01)
place_stack('where', ['W1', 'W2', 'W3', 'W4'], R); place_card('K6', 'where', L, 900, 900, -0.01)
place_stack('cost', ['X0', 'X1', 'X2', 'X3'], R); place_card('K7', 'cost', L, 900, 980, 0.008)
place_card('MY', 'many', R, 900, 800, 0.01)
place_card('M1', 'module', L, 1200, 1300, 0.0); bare('M1')
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E5', 'E6', 'E7'], 850)
place_card('HE', 'here', 850, 1000, 260, 0.0); bare('HE')
for _cid in [c for c in CLIPS if c not in STACK_OF]: del CLIPS[_cid]
