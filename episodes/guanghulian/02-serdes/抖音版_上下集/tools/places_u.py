# ---------- 02 抖音上集的摆放（按出场顺序左右交替） ----------
def bare(cid): CARDS[cid]['bare'] = True
place_card('P0', 'wires', L, 1000, 800, 0.0); bare('P0'); COLY[L] += 650
LAST[0] = 0
place_card('RT', 'route', R, 900, 700, 0.008)
place_stack('w', ['W1', 'W2'], L); place_card('K4', 'skew', R, 900, 1000, -0.008)
place_stack('q', ['Q2', 'Q3', 'Q4', 'Q5'], L); place_card('K3', 'pins', R, 900, 860, 0.008)
place_stack('l', ['L1', 'L2', 'L3'], L); place_card('K5', 'lanes', R, 900, 760, 0.01)
place_stack('n', ['N1', 'N2', 'N3', 'N4'], L); place_card('K1', 'serdes2', R, 900, 1250, -0.008)
place_card('P1', 'wires', L, 1000, 800, 0.0); bare('P1')
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2'], 850)
place_card('HE', 'here', 850, 1000, 260, 0.0); bare('HE')
for _cid in [c for c in CLIPS if c not in STACK_OF]: del CLIPS[_cid]
