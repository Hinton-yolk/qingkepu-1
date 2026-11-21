# V03 成片时间 → 场景时间（纯 Python，Blender 和 post.py 都用）。
# 第二幕（模型算候选）和第四幕前半（「去」进模型）压紧；其余原速。单调三次 Hermite（Fritsch–Carlson），变速平滑、不跳帧。
KEY = [(0.0, 4.4), (6.0, 10.4), (13.4, 19.6), (22.2, 28.4), (26.55, 34.5), (71.05, 79.0)]
FILM_DUR = KEY[-1][0]

def _slopes(xs, ys):
    n = len(xs); d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [0.0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if d[i] == 0: m[i] = m[i + 1] = 0.0; continue
        a, b = m[i] / d[i], m[i + 1] / d[i]; s = a * a + b * b
        if s > 9: k = 3 / s ** 0.5; m[i] = k * a * d[i]; m[i + 1] = k * b * d[i]
    return m
_X = [k[0] for k in KEY]; _Y = [k[1] for k in KEY]; _M = _slopes(_X, _Y)

def film_to_scene(ft):
    if ft <= _X[0]: return _Y[0] + (ft - _X[0]) * _M[0]
    if ft >= _X[-1]: return _Y[-1] + (ft - _X[-1]) * _M[-1]
    i = max(k for k in range(len(_X) - 1) if _X[k] <= ft)
    h = _X[i + 1] - _X[i]; u = (ft - _X[i]) / h
    h00 = 2 * u ** 3 - 3 * u ** 2 + 1; h10 = u ** 3 - 2 * u ** 2 + u; h01 = -2 * u ** 3 + 3 * u ** 2; h11 = u ** 3 - u ** 2
    return h00 * _Y[i] + h10 * h * _M[i] + h01 * _Y[i + 1] + h11 * h * _M[i + 1]

def scene_to_film(st):
    lo, hi = -5.0, FILM_DUR + 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if film_to_scene(mid) < st: lo = mid
        else: hi = mid
    return (lo + hi) / 2
