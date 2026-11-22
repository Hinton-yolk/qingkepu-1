#!/usr/bin/env python3
"""租一台 RunPod GPU 机器当「远程工作台」：传 bash 脚本上去后台跑、看日志、拉回文件，用完删掉。
本云端容器连不上 huggingface.co 等站点、也没有显卡时用它（例如在 pod 上装 ACE-Step 生成音乐）。

  python3 tools/runpod_exec.py up [--gpu "id1,id2"] [--image IMG] [--disk 80] [--max-hours 2] [--cloud SECURE] --yes
  python3 tools/runpod_exec.py run <任务名> <本地脚本.sh>      在 pod 上后台跑（工作目录 /w，日志 /w/out/logs/<任务名>.log）
  python3 tools/runpod_exec.py wait <任务名> [--timeout 3600]  等它跑完，打印日志尾和退出码
  python3 tools/runpod_exec.py status                         各任务状态 + /w/out 文件列表
  python3 tools/runpod_exec.py put <本地文件> <名字>            传到 pod 的 /w/in/<名字>
  python3 tools/runpod_exec.py get <相对 /w/out 的路径> <本地路径>
  python3 tools/runpod_exec.py down                           删 pod（另有看门狗：到 --max-hours 自己删）

状态（pod id、token）存在 out/runpod_exec.json。API key 由网络代理注入，这里只有占位值；建机 / 删机走 GraphQL（同 runpod_render_gql.py）。
"""
import base64, importlib.util, json, os, secrets, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('runpod_render_gql', os.path.join(HERE, 'runpod_render_gql.py'))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
R = G.R
STATE = os.path.join(R.REPO, 'out', 'runpod_exec.json')
IMAGE = 'python:3.11-slim-bookworm'   # small and quick to pull; ACE-Step's uv env brings its own torch + CUDA libs (the 10 GB pytorch image took 10+ min on one host)
GPUS = 'NVIDIA GeForce RTX 4090,NVIDIA GeForce RTX 3090,NVIDIA RTX A5000,NVIDIA L40S,NVIDIA RTX 6000 Ada Generation'

SRV = r'''
import http.server, json, os, subprocess, threading, time, urllib.request
TOK = os.environ['TOKEN']; W = '/w'; MAX = int(os.environ.get('MAX_SEC', '7200'))
for d in ('out/logs', 'jobs', 'in'): os.makedirs(f'{W}/{d}', exist_ok=True)
def watchdog():                       # delete this pod when the time is up, so a forgotten pod stops costing money
    time.sleep(MAX)
    try:
        q = json.dumps(dict(query='mutation { podTerminate(input: {podId: "%s"}) }' % os.environ.get('RUNPOD_POD_ID')))
        urllib.request.urlopen(urllib.request.Request('https://api.runpod.io/graphql', method='POST', data=q.encode(),
            headers={'Authorization': 'Bearer ' + os.environ.get('RUNPOD_API_KEY', ''), 'Content-Type': 'application/json'}), timeout=30)
    except Exception as e: open(W + '/watchdog.log', 'a').write(repr(e) + '\n')
    os._exit(0)
threading.Thread(target=watchdog, daemon=True).start()
JOBS = {}
def run(name, path):
    with open(f'{W}/out/logs/{name}.log', 'wb') as lf:
        p = subprocess.Popen(['bash', path], stdout=lf, stderr=subprocess.STDOUT, cwd=W)
        JOBS[name] = dict(done=False, code=None, t0=time.time()); code = p.wait()
        JOBS[name].update(done=True, code=code, t1=time.time())
def tail(name, n=3000):
    try: b = open(f'{W}/out/logs/{name}.log', 'rb').read(); return b[-n:].decode('utf-8', 'replace')
    except Exception: return ''
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def ok(self):
        if self.headers.get('X-Token') != TOK: self.send_error(403); return False
        return True
    def send(self, body, ctype='application/json'):
        self.send_response(200); self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if not self.ok(): return
        if self.path == '/status':
            files = []
            for root, _, fs in os.walk(W + '/out'):
                for f in fs: p = os.path.join(root, f); files.append([os.path.relpath(p, W + '/out'), os.path.getsize(p)])
            jobs = {k: dict(v, secs=round((v.get('t1') or time.time()) - v['t0']), tail=tail(k)) for k, v in JOBS.items()}
            self.send(json.dumps(dict(jobs=jobs, files=files)).encode())
        elif self.path.startswith('/out/'):
            p = os.path.realpath(os.path.join(W, 'out', self.path[5:]))
            if not p.startswith(W + '/out/') or not os.path.isfile(p): self.send_error(404); return
            self.send(open(p, 'rb').read(), 'application/octet-stream')
        else: self.send_error(404)
    def do_PUT(self):
        if not self.ok(): return
        n = int(self.headers['Content-Length']); data = self.rfile.read(n); kind, _, name = self.path.strip('/').partition('/')
        if not name or '/' in name or name.startswith('.'): self.send_error(400); return
        if kind == 'run':
            if name in JOBS and not JOBS[name]['done']: self.send_error(409); return
            path = f'{W}/jobs/{name}.sh'; open(path, 'wb').write(data); threading.Thread(target=run, args=(name, path), daemon=True).start()
        elif kind == 'in': open(f'{W}/in/{name}', 'wb').write(data)
        else: self.send_error(404); return
        self.send(b'{"ok":true}')
http.server.ThreadingHTTPServer(('0.0.0.0', 8000), H).serve_forever()
'''
POD_SH = 'mkdir -p /w && echo "$SRV_B64" | base64 -d > /w/srv.py && exec python3 /w/srv.py\n'
MUT = 'mutation($i: PodFindAndDeployOnDemandInput) { podFindAndDeployOnDemand(input: $i) { id costPerHr machine { gpuDisplayName } } }'


def state():
    if not os.path.exists(STATE): raise SystemExit('没有在用的 pod（先 up）')
    return json.load(open(STATE))


def http(method, path, data=None, timeout=60):
    s = state(); return R.pod_http(s['id'], s['token'], method, path, data, timeout=timeout)


def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return
    cmd = a[0]; opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    if cmd == 'up':
        if os.path.exists(STATE): raise SystemExit(f'已有 pod：{json.load(open(STATE))["id"]}（先 down）')
        if '--yes' not in a: raise SystemExit('要真的租卡，加 --yes')
        token = secrets.token_urlsafe(24); max_h = float(opt('--max-hours', 2))
        env = dict(TOKEN=token, SRV_B64=base64.b64encode(SRV.encode()).decode(), POD_SH_B64=base64.b64encode(POD_SH.encode()).decode(),
                   MAX_SEC=str(int(max_h * 3600)), NVIDIA_DRIVER_CAPABILITIES='all')
        base = dict(name=f'{R.PREFIX}exec', imageName=opt('--image', IMAGE), gpuCount=1, containerDiskInGb=int(opt('--disk', 80)), volumeInGb=0,
                    ports='8000/http', minVcpuCount=8, minMemoryInGb=32,
                    dockerArgs="bash -c 'echo $POD_SH_B64 | base64 -d > /pod.sh && bash /pod.sh'", env=[dict(key=k, value=v) for k, v in env.items()])
        pod = None
        for cloud in opt('--cloud', 'COMMUNITY,SECURE').split(','):   # --cloud SECURE: community hosts can be slow to install (apt 9 min, uv stuck on 2026-11-22)
            for gpu in opt('--gpu', GPUS).split(','):
                try: pod = G.gql(MUT, dict(i=dict(base, cloudType=cloud, gpuTypeId=gpu)))['podFindAndDeployOnDemand']
                except RuntimeError as e: print(f'{cloud} {gpu}: {str(e)[:160]}'); continue
                if pod: pod['gpu'] = gpu; break
            if pod: break
        if not pod: raise SystemExit('没租到卡')
        os.makedirs(os.path.dirname(STATE), exist_ok=True)
        json.dump(dict(id=pod['id'], token=token, cost=pod.get('costPerHr'), gpu=pod['gpu'], t0=time.time()), open(STATE, 'w'))
        print(f"建好 pod {pod['id']}：{pod['gpu']}，每小时 ${pod.get('costPerHr')}；等服务起来…", flush=True)
        for i in range(120):
            try: http('GET', '/status', timeout=20); print(f'服务已起来（{i * 10} 秒）'); return
            except Exception: time.sleep(10)
        raise SystemExit('20 分钟没起来；用 status 再看，或 down')
    if cmd == 'down':
        s = state(); G.api('DELETE', f"/pods/{s['id']}"); os.remove(STATE)
        mins = (time.time() - s.get('t0', time.time())) / 60
        print(f"已删除 pod {s['id']}；用了约 {mins:.0f} 分钟，约 ${(s.get('cost') or 0) * mins / 60:.2f}（以 RunPod 账单为准）"); return
    if cmd == 'run':
        print(http('PUT', f'/run/{a[1]}', open(a[2], 'rb').read()).decode()); return
    if cmd == 'put':
        print(http('PUT', f'/in/{a[2]}', open(a[1], 'rb').read(), timeout=300).decode()); return
    if cmd == 'get':
        os.makedirs(os.path.dirname(os.path.abspath(a[2])), exist_ok=True)
        open(a[2], 'wb').write(http('GET', '/out/' + a[1], timeout=300)); print('拉回', a[2], os.path.getsize(a[2])); return
    if cmd == 'status':
        st = json.loads(http('GET', '/status'))
        for k, v in st['jobs'].items(): print(f"[{k}] {'完成 code=' + str(v['code']) if v['done'] else '运行中'} {v['secs']} 秒")
        for f, n in st['files']: print(f'  {f}  {n}')
        return
    if cmd == 'wait':
        t0 = time.time(); lim = float(opt('--timeout', 3600))
        while time.time() - t0 < lim:
            try: v = json.loads(http('GET', '/status'))['jobs'].get(a[1])
            except Exception as e: v = None; print('连不上，重试', type(e).__name__, flush=True)
            if v and v['done']: print(v['tail'][-2500:]); print(f"== {a[1]} 结束 code={v['code']}，{v['secs']} 秒"); sys.exit(0 if v['code'] == 0 else 1)
            time.sleep(10)
        raise SystemExit('等待超时（任务仍在跑）')
    raise SystemExit(__doc__)


if __name__ == '__main__':
    main()
