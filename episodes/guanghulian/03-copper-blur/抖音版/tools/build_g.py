# 光互连 03 抖音无旁白版的时间表：python3 tools/build_g.py → 代码工程/split/g1.json、g2.json
# 秒数按分镜设计，吸附到 120 BPM 的 1/4 拍（0.125 s）上；画面读 D.cue、D.shots。没有配音：lines 只是给路线图（「快递」）和「一句话」打字用的虚拟句子。
import json
BPM = 120; q = 0.125; S = lambda x: round(round(x / q) * q, 3)
def line(i, text, t0, t1, kws={}):
    n = len(text); an = sorted([(text.index(w), t) for w, t in kws.items()] + [(0, t0), (n, t1)]); ch = []
    for j in range(n):
        a = max((p for p in an if p[0] <= j), key=lambda p: p[0]); b = min((p for p in an if p[0] > j), key=lambda p: p[0], default=(n, t1))
        ch.append(round(a[1] + (b[1] - a[1]) * (j - a[0]) / max(1, b[0] - a[0]), 3))
    return dict(id=i, t0=t0, t1=t1, clip=t0, text=text, ch=ch, sub=None, big=None, seg='nv', src='')
TK = lambda text, l, a=None, b=None: dict(text=text, line=l, **{'from': a}, to=b)
def build(name, shots, cue, take, dur, hud):
    cue = {k: S(v) for k, v in cue.items()}
    t_take = [s for s in shots if s['kind'] == 'take'][0]['t0']; t_route = [s for s in shots if s['kind'] == 'route'][0]['t0']
    lines = [line('r1', 'AI 芯片之间寄快递', t_route, t_route + 2, {'快递': t_route + 0.3})]
    lines += [line(f'z{i}', s, t_take + 0.2 + i * 0.6, t_take + 0.8 + i * 0.6) for i, s in enumerate(take)]
    shots = [dict(s, t0=S(s['t0'])) for s in shots]
    for k, s in enumerate(shots):
        s['paper'] = s['kind'] == 'take'; s['t1'] = shots[k + 1]['t0'] if k + 1 < len(shots) else dur
        if s['kind'] == 'route': s['first'] = 'r1'
        if s['kind'] == 'take': s['type'] = [TK('一句话带走', 'z0')] + [TK(x, f'z{i + 1}') for i, x in enumerate(take[1:])]
    D = dict(name=name, dur=dur, lines=lines, shots=shots, hudIn=S(hud), caps=[], bpm=BPM, novoice=True, cue=cue, stn=1)
    json.dump(D, open(f'代码工程/split/{name}.json', 'w'), ensure_ascii=False)
    print(name, dur, 's,', len(shots), 'shots')
B = lambda t0, text, hl=None, kicker=None, size=None: dict(kind='beat', t0=t0, text=text, hl=hl or [None] * len(text), kicker=kicker, **({'size': size} if size else {}))
build('g1', [dict(kind='cables', t0=0), dict(kind='route', t0=6), B(8, ['为什么会糊？', '每个比特都会拖尾巴'], [None, '拖尾巴']), dict(kind='tail', t0=10), dict(kind='glitch', t0=16),
             B(20, ['越快越糟？', '速度翻倍', '每个比特的时间减半'], [None, None, '时间减半']), dict(kind='faster', t0=22), dict(kind='cables2', t0=30), dict(kind='take', t0=36)],
      dict(tag1=1.5, tag2=2.5, ring1=3.5, morph=10.75, seq=12.5, sum=13.75, ana=14.75, photo=16.5, msg=17.75, rowA=22.25, rowB=23.25, same=24.75, bt0=26.0, hit=26.5, bt1=28.0, ring2=30.5, fiber2=32.5, rev=26.5),
      ['一句话带走', '越快，', '铜线能送的距离越短。'], 42.0, 6.5)
build('g2', [dict(kind='rack', t0=0), dict(kind='route', t0=6.5), B(8.5, ['把路修短'], ['修短'], '第 1 招'), dict(kind='short', t0=10), B(14, ['把路修好'], ['修好'], '第 2 招'), dict(kind='better', t0=15.5),
             B(19, ['在路上修信号'], ['修信号'], '第 3 招'), dict(kind='repair', t0=20.5), B(28, ['所以铜线没被淘汰', '便宜、可靠，短距离照样用'], ['没被淘汰', None]), dict(kind='rack2', t0=30), dict(kind='take', t0=36)],
      dict(mag=2.0, fiber=4.5, slide=11.75, swap=16.75, station=21.5, reveal=24.5, ring=30.5, far=32.5, rev=24.5),
      ['一句话带走', '修短、修好、路上修；', '修不动的，交给光。'], 42.0, 7.0)
