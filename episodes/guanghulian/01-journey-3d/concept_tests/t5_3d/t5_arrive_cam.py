# 结尾「亮起」相机：通道里的中景，缓慢推近。B 标记在画面下半，过桥和线槽在上半。
CAM_KEYS = [
    (0.0, V((5.00, -2.75, 1.45)), V((5.28, -1.60, 1.12))),
    (2.5, V((5.12, -2.45, 1.80)), V((5.22, -1.55, 0.95))),
]
LENS = [(0.0, 28), (2.5, 30)]
FSTOP = [(0.0, 4.0), (2.5, 4.0)]
def cam_fn(t):
    loc = S.hermite([(k[0], k[1]) for k in CAM_KEYS], t); tg = S.hermite([(k[0], k[2]) for k in CAM_KEYS], t)
    return dict(loc=loc, tgt=tg, lens=S.hermite_s(LENS, t), fstop=S.hermite_s(FSTOP, t))
_dbg = os.environ.get('T5_DBG')
if _dbg:
    _v = [float(x) for x in _dbg.split(',')]
    def cam_fn(t): return dict(loc=V(_v[0:3]), tgt=V(_v[3:6]), lens=_v[6], fstop=_v[7] if len(_v) > 7 else 4.0)
