"""PLATEAU CityGML (LOD0 roof edge + measured height) -> model.json + stats.json for one site.
Model units: model metres at 1:1000 (1 unit = 1000 real metres), x east, z south, origin at the site centre.
Every on-screen number is computed here, from the same buildings that are on the table (see FACTS.md)."""
import json, math, os, sys
import numpy as np
from lxml import etree

NS = {'bldg': 'http://www.opengis.net/citygml/building/2.0', 'gml': 'http://www.opengis.net/gml'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITES = {
    'A': dict(name='高岛平团地', jp='高島平団地', ward='板桥区', gml=['53395542', '53395543'], lat=35.78675, lon=139.66138, r=230),
    'B': dict(name='高圆寺', jp='高円寺', ward='杉并区', gml=['53394541', '53394542'], lat=35.7046, lon=139.6492, r=330),
    'C': dict(name='新宿西口', jp='西新宿', ward='新宿区', gml=['53394525', '53394535'], lat=35.6895, lon=139.6925, r=420),
}
SCALE = 1000.0
# usage codes (PLATEAU 建築物 usage codelist): 401 業務 402 商業 403 宿泊 411 住宅 412 共同住宅 413 店舗等併用住宅 414 店舗等併用共同住宅
DWELLING_M2 = 60.0      # floor area per apartment (estimate)
OFFICE_M2 = 150.0       # floor area per office access point (estimate)


def area(r):
    a = 0.0
    for i in range(len(r)):
        x0, z0 = r[i]; x1, z1 = r[(i + 1) % len(r)]
        a += x0 * z1 - x1 * z0
    return a / 2


def obb(ring):
    """length and width of the minimum-area rectangle around a footprint (metres)"""
    P = np.array(ring); best = None
    for i in range(len(P)):
        e = P[(i + 1) % len(P)] - P[i]; n = np.hypot(*e)
        if n < 1e-6: continue
        u = e / n; v = np.array([-u[1], u[0]])
        a, b = P @ u, P @ v
        L, Wd = a.max() - a.min(), b.max() - b.min()
        if best is None or L * Wd < best[0] * best[1]: best = (L, Wd)
    L, Wd = best
    return max(L, Wd), min(L, Wd)


BAY_M = 6.5             # one apartment per 6.5 m of a slab's long side, per floor (single-loaded slab, estimate)


def routers(usage, floors, foot, ring=None):
    floor_area = foot * max(1, floors)
    if usage in ('412', '414') and ring is not None:
        L, Wd = obb(ring)
        if Wd <= 16:                            # a slab: count bays along the long side
            return max(1, round(L / BAY_M) * max(1, floors))
    if usage in ('411',):                       # a house: one household
        return 1
    if usage in ('412', '414'):                 # apartments
        return max(1, round(floor_area / DWELLING_M2))
    if usage in ('413',):
        return 2
    if usage in ('401', '402', '403'):          # offices, shops, hotels: access points
        return max(1, round(floor_area / OFFICE_M2))
    return max(0, round(floor_area / 400.0))    # sheds, public, unknown: few


def main(key):
    S = SITES[key]
    lat0, lon0, R = S['lat'], S['lon'], S['r']
    kx = math.cos(math.radians(lat0)) * 111320.0
    kz = 110574.0
    B, P = [], []
    paths = [os.path.join(ROOT, 'data', 'udx', 'bldg', f'{g}_bldg_6697_op.gml') for g in S['gml']]
    for _, el in (ev for path in paths for ev in etree.iterparse(path, tag='{%s}Building' % NS['bldg'])):
        h = el.findtext('bldg:measuredHeight', namespaces=NS)
        if h is None:
            el.clear(); continue
        h = float(h)
        if h <= 0 or h > 700:
            el.clear(); continue
        usage = el.findtext('bldg:usage', namespaces=NS) or ''
        st = el.findtext('bldg:storeysAboveGround', namespaces=NS)
        floors = int(st) if st and st.isdigit() and 0 < int(st) < 200 else max(1, round(h / 3.2))   # 9999 = unknown in PLATEAU
        rings = []
        for lr in el.iterfind('bldg:lod0RoofEdge//gml:Polygon', namespaces=NS):
            for ring_el, hole in [(lr.find('gml:exterior//gml:posList', NS), False)] + [(x, True) for x in lr.iterfind('gml:interior//gml:posList', NS)]:
                if ring_el is None: continue
                v = np.array(ring_el.text.split(), float).reshape(-1, 3)
                xz = np.stack([(v[:, 1] - lon0) * kx, -(v[:, 0] - lat0) * kz], 1)
                if len(xz) > 3 and np.allclose(xz[0], xz[-1]): xz = xz[:-1]
                rings.append((xz, hole))
            break
        el.clear()
        if not rings: continue
        ext = rings[0][0]
        c = ext.mean(0)
        if math.hypot(*c) > R: continue
        foot = abs(area(ext.tolist()))
        if foot < 6: continue
        bi = len(B)
        n = routers(usage, floors, foot, ext.tolist())
        slab = obb(ext.tolist())[1] <= 16
        B.append(dict(h=round(h, 2), usage=usage, floors=floors, foot=round(foot, 1), routers=n, slab=slab,
                      c=[round(c[0] / SCALE, 5), round(c[1] / SCALE, 5)]))
        P.append([bi, round(h / SCALE, 5), [[[round(x / SCALE, 5), round(z / SCALE, 5)] for x, z in r] for r, _ in rings]])
    tot = sum(b['routers'] for b in B)
    homes = sum(b['routers'] for b in B if b['usage'] in ('411', '412', '413', '414'))
    tallest = max(range(len(B)), key=lambda i: B[i]['h'])
    # the pick-out for A: the largest apartment slab near the centre
    apt = [i for i, b in enumerate(B) if b['usage'] in ('412', '414') and b['floors'] >= 10 and b['slab']] or [i for i, b in enumerate(B) if b['usage'] in ('412', '414')]
    pick = max(apt, key=lambda i: B[i]['routers'] - 40 * math.hypot(*B[i]['c']) * SCALE / R) if apt else tallest
    size = [round(2 * R / SCALE + 0.02, 4)] * 2
    out = os.path.join(ROOT, 'data', key); os.makedirs(out, exist_ok=True)
    json.dump({'size': size, 'b': [[b['h'], b['floors'], b['routers'], int(b['usage'] or 0)] for b in B], 'p': P},
              open(os.path.join(out, 'model.json'), 'w'), separators=(',', ':'))
    stats = dict(site=S, buildings=len(B), routers=tot, homes=homes, area_km2=round(math.pi * R * R / 1e6, 3),
                 tallest=dict(i=tallest, h=B[tallest]['h'], floors=B[tallest]['floors']),
                 pick=dict(i=pick, h=B[pick]['h'], floors=B[pick]['floors'], routers=B[pick]['routers'], foot=B[pick]['foot'], c=B[pick]['c'], length_m=round(obb([[x * SCALE, z * SCALE] for x, z in P[pick][2][0]])[0], 1)),
                 method=dict(dwelling_m2=DWELLING_M2, office_m2=OFFICE_M2, slab_bay_m=BAY_M, scale=f'1:{int(SCALE)}'),
                 source='国土交通省 PLATEAU 3D 都市模型（CC BY 4.0 兼容），bldg ' + ', '.join(S['gml']))
    json.dump(stats, open(os.path.join(out, 'stats.json'), 'w'), ensure_ascii=False, indent=1)
    print(key, S['name'], f"{len(B)} buildings, ≈{tot} routers ({homes} homes), tallest {B[tallest]['h']} m, pick #{pick}: {B[pick]['floors']}F {B[pick]['routers']} homes")


if __name__ == '__main__':
    for k in (sys.argv[1:] or 'ABC'):
        main(k)
