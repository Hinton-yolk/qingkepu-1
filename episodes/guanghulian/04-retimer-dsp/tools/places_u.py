# ---------- 04 上集的摆放（按出场顺序左右交替） ----------
def bare(cid): CARDS[cid]['bare'] = True
place_card('P0', 'eqapp', L, 1000, 1000, 0.0); bare('P0'); COLY[L] += 350
LAST[0] = 0
place_card('RT', 'route', R, 900, 700, 0.008)
place_card('H0', 'hook4', L, 900, 760, -0.008)
place_stack('eq', ['A0', 'A1', 'A2'], R); place_card('K2', 'eq', R, 900, 1200, -0.008)
place_card('WH', 'whole', L, 900, 1000, 0.008)
place_stack('nm', ['B5', 'B6'], L)
place_stack('ret', ['C0', 'C1', 'C2'], R); place_card('K3', 'retimer', R, 900, 1100, 0.008)
place_card('HB', 'hub', L, 900, 760, -0.01)
place_stack('rname', ['R1', 'R2', 'R3'], L); place_card('K4', 'redriver', R, 900, 1000, -0.008)
place_card('P1', 'eqapp', L, 1000, 1000, 0.0); bare('P1')
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'E1', 'E2', 'E3', 'E4', 'E7'], 850)
place_card('HE', 'here', 850, 1000, 260, 0.0); bare('HE')
for _cid in [c for c in CLIPS if c not in STACK_OF]: del CLIPS[_cid]
