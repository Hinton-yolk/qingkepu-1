# ---------- 02 抖音下集的摆放（按出场顺序左右交替） ----------
def bare(cid): CARDS[cid]['bare'] = True
place_card('P0', 'chat', L, 700, 800, 0.0); bare('P0'); COLY[L] += 650
LAST[0] = 0
place_card('RT', 'route', R, 900, 700, 0.008)
place_card('K6', 'clock', L, 900, 700, -0.008)
place_stack('o', ['O8', 'O9'], R); place_card('CL', 'clap', L, 900, 720, 0.01)
place_card('SC', 'scramble', R, 900, 1100, -0.008)
place_stack('h', ['H2'], L); place_card('K7', 'double', R, 900, 1050, 0.008)
place_stack('h6', ['H6'], L)
place_card('P1', 'chat', L, 700, 800, 0.0); bare('P1')
END_TOP = max(COLY.values()) + 100; COLY[850] = END_TOP; LAST[0] = END_TOP
place_stack('end', ['E0', 'X4', 'X5'], 850)
place_card('HE', 'here', 850, 1000, 260, 0.0); bare('HE')
for _cid in [c for c in CLIPS if c not in STACK_OF]: del CLIPS[_cid]
