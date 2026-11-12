# 结尾「亮起」相机：通道里的中景，缓慢推近。B 标记在画面下半，过桥和线槽在上半。
CAM_KEYS = [
    (0.0, V((3.00, 0.50, 1.00)), V((4.70, -0.80, 1.85))),
    (2.5, V((3.30, 0.45, 1.00)), V((4.95, -0.80, 1.60))),
]
LENS = [(0.0, 20), (2.5, 24)]
FSTOP = [(0.0, 2.0), (2.5, 2.0)]
def cam_fn(t):
    loc = S.hermite([(k[0], k[1]) for k in CAM_KEYS], t); tg = S.hermite([(k[0], k[2]) for k in CAM_KEYS], t)
    return dict(loc=loc, tgt=tg, lens=S.hermite_s(LENS, t), fstop=S.hermite_s(FSTOP, t))
_dbg = os.environ.get('T5_DBG')
if _dbg:
    _v = [float(x) for x in _dbg.split(',')]
    def cam_fn(t): return dict(loc=V(_v[0:3]), tgt=V(_v[3:6]), lens=_v[6], fstop=_v[7] if len(_v) > 7 else 4.0)
