#!/usr/bin/env python3
"""Poly Haven 素材下载器（HDRI / 贴图 / 模型，全部 CC0）。

API：https://api.polyhaven.com （不需要 key；条款要求请求带能标识软件名的 User-Agent，见下面 UA）。
素材是 CC0，用在视频里不需要署名；条款只要求「在产品里实时展示 API 内容」时注明来源，我们的用法不涉及。

缓存目录：assets/polyhaven/<类型>/<id>/<分辨率>/（不进仓库，见 .gitignore），同目录写 manifest.json。
资产列表在 assets/polyhaven/_index_<类型>.json 缓存 24 小时，避免重复请求。

用法：
  python3 tools/polyhaven.py search textures metal brushed      # 按关键词搜（名字、标签、分类）
  python3 tools/polyhaven.py search hdris studio --limit 10
  python3 tools/polyhaven.py search models cable
  python3 tools/polyhaven.py info metal_plate                   # 看详情和有哪些贴图
  python3 tools/polyhaven.py get metal_plate --res 2k           # 下载贴图（默认：diff, rough, nor_gl, metal, disp, ao）
  python3 tools/polyhaven.py get studio_small_09 --res 2k       # HDRI（.hdr）
  python3 tools/polyhaven.py get <模型id> --res 1k --format gltf # 模型（含它引用的贴图）
下载后会核对 md5。打印的最后一行是本地目录，Blender 里用 tools/polyhaven_blender.py 加载。
"""
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'assets', 'polyhaven')
API = 'https://api.polyhaven.com'
UA = 'kepu-studio-asset-fetch/1.0'
DEFAULT_MAPS = ['Diffuse', 'Rough', 'nor_gl', 'Metal', 'Displacement', 'AO']
_last = [0.0]


def get_json(path):
    wait = 0.25 - (time.time() - _last[0])        # 两次请求至少间隔 0.25 秒
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(API + path, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        _last[0] = time.time()
        return json.load(r)


def download(url, dest, md5=None):
    if os.path.exists(dest) and md5 and hashlib.md5(open(dest, 'rb').read()).hexdigest() == md5:
        return 'cached'
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=300) as r, open(dest + '.part', 'wb') as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
    if md5:
        got = hashlib.md5(open(dest + '.part', 'rb').read()).hexdigest()
        if got != md5:
            os.remove(dest + '.part')
            raise SystemExit(f'md5 不符：{url}')
    os.replace(dest + '.part', dest)
    return 'downloaded'


def index(kind):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, f'_index_{kind}.json')
    if os.path.exists(p) and time.time() - os.path.getmtime(p) < 86400:
        return json.load(open(p))
    d = get_json(f'/assets?t={kind}')
    json.dump(d, open(p, 'w'))
    return d


def cmd_search(a):
    d = index(a.type)
    words = [w.lower() for w in a.words]
    hits = []
    for aid, v in d.items():
        hay = ' '.join([aid, v.get('name', '')] + v.get('tags', []) + v.get('categories', [])).lower()
        score = sum(hay.count(w) for w in words)
        if all(w in hay for w in words):
            hits.append((score, v.get('download_count', 0), aid, v))
    hits.sort(key=lambda h: (-h[0], -h[1]))
    for _, dl, aid, v in hits[:a.limit]:
        dims = v.get('dimensions')
        size = f"{dims[0] / 1000:.2f}×{dims[1] / 1000:.2f} m" if dims else ''
        print(f"{aid:32s} {v.get('name', '')[:34]:34s} {size:14s} 下载 {dl}  分类 {','.join(v.get('categories', [])[:4])}")
    print(f'共 {len(hits)} 个匹配（显示前 {min(len(hits), a.limit)} 个）')


def cmd_info(a):
    info = get_json(f'/info/{a.id}')
    files = get_json(f'/files/{a.id}')
    print(json.dumps({k: info.get(k) for k in ('name', 'type', 'categories', 'tags', 'dimensions', 'authors', 'description', 'max_resolution')}, ensure_ascii=False, indent=1))
    print('可下载：')
    for k, v in files.items():
        if isinstance(v, dict):
            print(f'  {k}: 分辨率 {sorted(v.keys())}')


def cmd_get(a):
    info = get_json(f'/info/{a.id}')
    files = get_json(f'/files/{a.id}')
    kind = {0: 'hdris', 1: 'textures', 2: 'models'}[info['type']]
    out = os.path.join(CACHE, kind, a.id, a.res)
    got = {}
    if kind == 'hdris':
        f = files['hdri'][a.res][a.format or 'hdr']
        dest = os.path.join(out, os.path.basename(f['url']))
        print(download(f['url'], dest, f.get('md5')), dest)
        got['hdri'] = os.path.basename(dest)
    elif kind == 'textures':
        maps = a.maps.split(',') if a.maps else DEFAULT_MAPS
        for m in maps:
            if m not in files or a.res not in files[m]:
                continue
            fmt = a.format or ('exr' if m == 'Displacement' and 'exr' in files[m][a.res] else 'jpg')
            if fmt not in files[m][a.res]:
                fmt = next(iter(files[m][a.res]))
            f = files[m][a.res][fmt]
            dest = os.path.join(out, os.path.basename(f['url']))
            print(download(f['url'], dest, f.get('md5')), dest)
            got[m] = os.path.basename(dest)
    else:
        fmt = a.format or 'gltf'
        f = files[fmt][a.res][fmt]
        dest = os.path.join(out, os.path.basename(f['url']))
        print(download(f['url'], dest, f.get('md5')), dest)
        got['model'] = os.path.basename(dest)
        for rel, inc in f.get('include', {}).items():
            d2 = os.path.join(out, rel)
            print(download(inc['url'], d2, inc.get('md5')), d2)
    manifest = {
        'id': a.id, 'name': info.get('name'), 'type': kind, 'resolution': a.res,
        'license': 'CC0 (Poly Haven)', 'authors': info.get('authors'),
        'dimensions_mm': info.get('dimensions'), 'files': got,
        'source': f'https://polyhaven.com/a/{a.id}', 'fetched': time.strftime('%Y-%m-%d'),
    }
    json.dump(manifest, open(os.path.join(out, 'manifest.json'), 'w'), ensure_ascii=False, indent=1)
    print(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    s = sp.add_parser('search')
    s.add_argument('type', choices=['hdris', 'textures', 'models'])
    s.add_argument('words', nargs='+')
    s.add_argument('--limit', type=int, default=15)
    s.set_defaults(fn=cmd_search)
    i = sp.add_parser('info')
    i.add_argument('id')
    i.set_defaults(fn=cmd_info)
    g = sp.add_parser('get')
    g.add_argument('id')
    g.add_argument('--res', default='2k')
    g.add_argument('--format', default=None, help='hdr / exr / jpg / png / gltf / blend / fbx')
    g.add_argument('--maps', default=None, help='逗号分隔，例如 Diffuse,Rough,nor_gl')
    g.set_defaults(fn=cmd_get)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    sys.exit(main())
