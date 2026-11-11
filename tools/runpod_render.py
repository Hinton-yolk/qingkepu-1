#!/usr/bin/env python3
"""在 RunPod 上租 GPU 渲 Blender：建 pod → 上传场景 → 分段渲染 → 拉回 PNG → 删 pod。全程只走 HTTPS。

用法：
  python3 tools/runpod_render.py plan  <jobs.json> [--pods N]          只打印分配和预估费用，不花钱
  python3 tools/runpod_render.py run   <jobs.json> [--pods N] [--gpu "NVIDIA GeForce RTX 4090"]
                                       [--cloud COMMUNITY|SECURE] [--max-hours 2] [--yes]
  python3 tools/runpod_render.py list                                 列出账号里所有 pod
  python3 tools/runpod_render.py kill-all                             删掉所有 kepu- 开头的 pod（兜底）

jobs.json：
  {"scene_dir": "相对仓库根的目录（里面有 shot_open.py、assets/ 等，整个打包上传）",
   "script": "shot_open.py",
   "out_dir": "本地输出目录（相对仓库根）",
   "sec_per_unit": 8,          # 一张 4090 每个单位（约一帧）预计秒数，只用于估价
   "tasks": [{"args": ["A", "{out}/seq", "1080", "1920", "64", "cycles", "gpu", "seq", "fs=1", "fe=12"], "units": 12}, ...]}
  args 是 blender `--` 后面的参数；{out} 会换成 pod 上的输出目录。

API key：不在这里存。云端会话里由网络代理注入 rest.runpod.io 的 Authorization 头（request_credential 保存），
  所以这里发的是占位值；在自己电脑上跑时设环境变量 RUNPOD_API_KEY。
安全：① 本脚本退出（包括出错、Ctrl-C）时删掉自己建的 pod，除非 --keep；② 每个 pod 自带看门狗，
  到 --max-hours 用 pod 自己的 RUNPOD_API_KEY 删掉自己（这一条未在真机上验证）；③ kill-all 兜底。
"""
import base64, io, json, os, secrets, sys, tarfile, time, urllib.error, urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://rest.runpod.io/v1'
KEY = os.environ.get('RUNPOD_API_KEY', 'proxy-injected')
BLENDER_URL = 'https://download.blender.org/release/Blender5.2/blender-5.2.3-linux-x64.tar.xz'
IMAGE = 'python:3.11-slim-bookworm'
PREFIX = 'kepu-'
UA = 'render-client/1.0'          # Cloudflare 会拦 Python 默认的 User-Agent（error code 1010）
STATE = os.path.join(REPO, 'out', 'runpod_state.json')

# ---------- pod 上跑的东西 ----------
SRV_PY = r'''
import http.server, json, os, threading, time, urllib.request
TOK = os.environ['TOKEN']; W = '/w'; MAX = int(os.environ.get('MAX_SEC', '7200'))
def watchdog():                      # 到时间就删掉自己，防止忘了关机一直扣钱
    time.sleep(MAX)
    for url, m in ((f"https://rest.runpod.io/v1/pods/{os.environ.get('RUNPOD_POD_ID')}", 'DELETE'),):
        try: urllib.request.urlopen(urllib.request.Request(url, method=m, headers={'Authorization': 'Bearer ' + os.environ.get('RUNPOD_API_KEY', '')}), timeout=30)
        except Exception as e: open(W + '/watchdog.log', 'a').write(repr(e) + '\n')
    os._exit(0)
threading.Thread(target=watchdog, daemon=True).start()
def rd(p, n=None):
    try:
        b = open(p, 'rb').read(); return (b[-n:] if n else b).decode('utf-8', 'replace')
    except Exception: return ''
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def auth(self):
        if self.headers.get('X-Token') != TOK: self.send_error(403); return False
        return True
    def send(self, body, ctype='application/json'):
        self.send_response(200); self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if not self.auth(): return
        if self.path == '/status':
            files = []
            for root, _, fs in os.walk(W + '/out'):
                for f in fs:
                    p = os.path.join(root, f); files.append([os.path.relpath(p, W + '/out'), os.path.getsize(p)])
            st = dict(stage=rd(W + '/stage').strip() or 'setup', cur=rd(W + '/cur').strip(), fails=rd(W + '/fails'),
                      files=files, log=rd(W + '/render.log', 1500), setup=rd(W + '/setup.log', 600), has_bundle=os.path.exists(W + '/bundle.tgz'))
            self.send(json.dumps(st).encode())
        elif self.path.startswith('/out/'):
            p = os.path.realpath(os.path.join(W, 'out', self.path[5:]))
            if not p.startswith(W + '/out/') or not os.path.isfile(p): self.send_error(404); return
            self.send(open(p, 'rb').read(), 'application/octet-stream')
        else: self.send_error(404)
    def do_PUT(self):
        if not self.auth(): return
        if self.path != '/bundle': self.send_error(404); return
        n = int(self.headers['Content-Length']); data = self.rfile.read(n)
        open(W + '/bundle.part', 'wb').write(data); os.replace(W + '/bundle.part', W + '/bundle.tgz'); self.send(b'{"ok":true}')
http.server.ThreadingHTTPServer(('0.0.0.0', 8000), H).serve_forever()
'''
POD_SH = r'''
mkdir -p /w/out; cd /w
echo "$SRV_PY_B64" | base64 -d > /w/srv.py; python3 /w/srv.py &
export DEBIAN_FRONTEND=noninteractive
echo apt > /w/stage
apt-get update -qq >>/w/setup.log 2>&1
apt-get install -y -qq --no-install-recommends curl ca-certificates xz-utils libxrender1 libxxf86vm1 libxfixes3 libxi6 libxkbcommon0 \
  libxkbcommon-x11-0 libsm6 libice6 libx11-6 libxext6 libgl1 libegl1 libglib2.0-0 >>/w/setup.log 2>&1
echo download_blender > /w/stage
curl -sSL "$BLENDER_URL" | tar -xJ -C /w >>/w/setup.log 2>&1 && mv /w/blender-*-linux-x64 /w/bl
nvidia-smi >>/w/setup.log 2>&1
echo wait_bundle > /w/stage
while [ ! -f /w/bundle.tgz ]; do sleep 2; done
mkdir -p /w/scene && tar xzf /w/bundle.tgz -C /w/scene
echo rendering > /w/stage
echo "$TASKS_B64" | base64 -d > /w/tasks.txt
i=0
while IFS= read -r line; do
  i=$((i+1)); echo "$i/$(wc -l < /w/tasks.txt)" > /w/cur
  /w/bl/blender -b --python-exit-code 1 --python "/w/scene/$SCRIPT" -- $line >> /w/render.log 2>&1 || echo "task $i failed: $line" >> /w/fails
done < /w/tasks.txt
echo done > /w/stage
sleep infinity
'''

# ---------- 本地 ----------
def api(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            t = r.read(); return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f'RunPod API {method} {path} → {e.code}: {e.read().decode()[:500]}')

def pod_http(pid, token, method, path, data=None, timeout=90):
    req = urllib.request.Request(f'https://{pid}-8000.proxy.runpod.net{path}', method=method, data=data, headers={'X-Token': token, 'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r: return r.read()

def split(tasks, n):
    """按 units 从大到小，每次给当前最轻的 pod（LPT），各 pod 的工作量尽量平均"""
    bins = [[0, []] for _ in range(n)]
    for t in sorted(tasks, key=lambda t: -t.get('units', 1)):
        b = min(bins, key=lambda b: b[0]); b[0] += t.get('units', 1); b[1].append(t)
    return [b for b in bins if b[1]]

def bundle(scene_dir):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as tf:
        for name in sorted(os.listdir(scene_dir)):
            if name in ('out', 'render_package_win', 'lookdev_package_win', '__pycache__'): continue
            tf.add(os.path.join(scene_dir, name), arcname=name)
    return buf.getvalue()

def load_jobs(path):
    J = json.load(open(path)); J['scene_dir'] = os.path.join(REPO, J['scene_dir']); J['out_dir'] = os.path.join(REPO, J['out_dir']); return J

def plan(J, n, price):
    bins = split(J['tasks'], n); spu = J.get('sec_per_unit', 8); setup = 2 * 60      # 冒烟测试实测：装环境 + 下载 Blender 约 1 分钟
    worst = max(b[0] for b in bins) * spu + len(max(bins, key=lambda b: b[0])[1]) * 40 + setup
    total_gpu_s = sum(b[0] * spu + len(b[1]) * 40 + setup for b in bins)
    for i, (u, ts) in enumerate(bins): print(f'  pod {i}: {len(ts)} 个任务，{u} 单位')
    print(f'预计墙钟 {worst / 60:.0f} 分钟；GPU 总时长 {total_gpu_s / 3600:.2f} 小时；'
          f'按每卡每小时 ${price} 估约 ${total_gpu_s / 3600 * price:.2f}（含每台约 2 分钟装环境；按秒计费）')
    return bins

def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return
    cmd = a[0]; opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    if cmd == 'list':
        for p in api('GET', '/pods'): print(p.get('id'), p.get('name'), p.get('desiredStatus'), p.get('costPerHr'))
        return
    if cmd == 'kill-all':
        for p in api('GET', '/pods'):
            if str(p.get('name', '')).startswith(PREFIX): api('DELETE', f"/pods/{p['id']}"); print('已删', p['id'], p.get('name'))
        return
    J = load_jobs(a[1]); n = int(opt('--pods', 4)); gpu = opt('--gpu', 'NVIDIA GeForce RTX 4090,NVIDIA GeForce RTX 5090,NVIDIA GeForce RTX 3090,NVIDIA L40S,NVIDIA RTX 6000 Ada Generation')
    cloud = opt('--cloud', 'COMMUNITY'); max_h = float(opt('--max-hours', 2)); price = float(opt('--price', 0.40))
    bins = plan(J, n, price)
    if cmd == 'plan': return
    if '--yes' not in a: raise SystemExit('要真的租卡，加 --yes（先用 plan 看费用）')
    data = bundle(J['scene_dir']); print(f'场景包 {len(data) / 1e6:.1f} MB')
    srv_b64 = base64.b64encode(SRV_PY.encode()).decode(); pods = []
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    try:
        for i, (_, ts) in enumerate(bins):
            token = secrets.token_urlsafe(24)
            lines = '\n'.join(' '.join(x.replace('{out}', '/w/out') for x in t['args']) for t in ts) + '\n'
            body = dict(name=f'{PREFIX}{i}', imageName=IMAGE, gpuTypeIds=gpu.split(','), gpuTypePriority='custom', gpuCount=1, cloudType=cloud,
                        containerDiskInGb=30, ports=['8000/http'], dockerEntrypoint=['bash', '-c'], dockerStartCmd=[POD_SH],
                        env=dict(TOKEN=token, SRV_PY_B64=srv_b64, TASKS_B64=base64.b64encode(lines.encode()).decode(),
                                 SCRIPT=J.get('script', 'shot_open.py'), BLENDER_URL=BLENDER_URL, MAX_SEC=str(int(max_h * 3600)),
                                 NVIDIA_DRIVER_CAPABILITIES='all'))
            try: p = api('POST', '/pods', body)
            except SystemExit as e:                     # Community 没空卡时换 Secure（贵一些）
                if 'no instances' not in str(e) or cloud == 'SECURE' or '--no-secure' in a: raise
                print('Community Cloud 没空卡，改用 Secure Cloud'); body['cloudType'] = 'SECURE'; p = api('POST', '/pods', body)
            pods.append(dict(id=p['id'], token=token, cost=p.get('costPerHr'), done=False, uploaded=False, got={}))
            print(f"建好 pod {i}: {p['id']}  每小时 ${p.get('costPerHr')}  {(p.get('machine') or {}).get('gpuTypeId') or p.get('gpuTypeId') or '?'}  {body['cloudType']}")
            json.dump([dict(id=q['id'], token=q['token']) for q in pods], open(STATE, 'w'))
        t0 = time.time(); last = {}
        while not all(q['done'] for q in pods):
            if time.time() - t0 > max_h * 3600: raise SystemExit('超过 --max-hours，停止')
            for q in pods:
                if q['done']: continue
                try: st = json.loads(pod_http(q['id'], q['token'], 'GET', '/status', timeout=30))
                except Exception as e: st = dict(stage=f'连不上（{type(e).__name__}，pod 可能还在启动）', files=[])
                if st.get('has_bundle'): q['uploaded'] = True
                elif not q['uploaded'] and 'has_bundle' in st:      # 服务一起来就传，和装环境并行
                    pod_http(q['id'], q['token'], 'PUT', '/bundle', data, timeout=95); q['uploaded'] = True; print(q['id'], '场景已上传')
                for rel, size in st.get('files', []):       # 渲好一张拉一张
                    dst = os.path.join(J['out_dir'], rel)
                    if q['got'].get(rel) == size or size < 10000 and rel.endswith('.png'): continue   # 大小变了（还在写、或日志又长了）就重拉
                    if os.path.exists(dst) and os.path.getsize(dst) == size: q['got'][rel] = size; continue
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    try: open(dst, 'wb').write(pod_http(q['id'], q['token'], 'GET', '/out/' + rel)); q['got'][rel] = size
                    except Exception as e: print('下载失败，下轮重试', rel, e)
                msg = f"[{(time.time() - t0) / 60:5.1f} 分] {q['id']} {st.get('stage')} {st.get('cur', '')} 已拉回 {len(q['got'])}"
                if st.get('fails'): msg += ' 失败：' + st['fails'].strip().replace('\n', ' | ')[:300]
                if last.get(q['id']) != msg: print(msg, flush=True); last[q['id']] = msg
                if st.get('stage') == 'done' and all(q['got'].get(f[0]) == f[1] for f in st['files'] if not (f[0].endswith('.png') and f[1] < 10000)):
                    if st.get('log'): open(os.path.join(J['out_dir'], f"log_{q['id']}.txt"), 'w').write(st['log'] + '\n---setup---\n' + st.get('setup', ''))
                    api('DELETE', f"/pods/{q['id']}"); q['done'] = True; print(q['id'], '完成，已删除')
            time.sleep(15)
        spent = sum((q['cost'] or 0) for q in pods) * (time.time() - t0) / 3600
        print(f'全部完成：墙钟 {(time.time() - t0) / 60:.1f} 分钟，约 ${spent:.2f}（上限估计，按秒计费，以 RunPod 账单为准）')
    finally:
        if '--keep' not in a:
            for q in pods:
                if not q['done']:
                    try: api('DELETE', f"/pods/{q['id']}"); print('收尾删除', q['id'])
                    except SystemExit as e: print('删除失败，请运行 kill-all：', e)

if __name__ == '__main__':
    main()
