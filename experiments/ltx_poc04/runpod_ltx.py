#!/usr/bin/env python3
"""在 RunPod 上跑 LTX-2.5 Layout-To-Render（IC-LoRA）：建一台 pod → 装 LTX-2 → 下载权重 → 上传输入 → 生成 → 拉回 → 删 pod。

用法：
  python3 runpod_ltx.py run <输入目录> <输出目录> [--gpu "NVIDIA H100 80GB HBM3,..."] [--max-hours 1.5] [--yes]
  python3 runpod_ltx.py list | kill-all

输入目录里要有 run.sh（在 pod 上执行，输出写到 /w/out），以及它用到的文件（灰模视频、关键帧）。

- API key：由云端会话的网络代理注入 rest.runpod.io 的 Authorization 头，这里只发占位值。
- Hugging Face token：**不经过本机**。pod 的环境变量写成 {{ RUNPOD_SECRET_hf_token }}，由 RunPod 从用户在控制台建的
  Secret 里替换，pod 直接从 Hugging Face 下载权重（LTX-2.5 是 gated 模型，需要 token）。
- 权重每次开机重新下载（用户 2026-11-14 定：测试阶段不建网络存储）。
- 安全：本脚本退出时删掉自己建的 pod（除非 --keep）；pod 自带看门狗，到 --max-hours 自己删除；kill-all 兜底。
"""
import base64
import io
import json
import os
import secrets
import sys
import tarfile
import time
import urllib.error
import urllib.request

API = 'https://rest.runpod.io/v1'
KEY = os.environ.get('RUNPOD_API_KEY', 'proxy-injected')
UA = 'render-client/1.0'
PREFIX = 'kepu-ltx-'
IMAGE = 'python:3.12-slim-bookworm'
GPUS = 'NVIDIA H100 80GB HBM3,NVIDIA H100 NVL,NVIDIA H100 PCIe,NVIDIA A100-SXM4-80GB,NVIDIA A100 80GB PCIe'

SRV_PY = r'''
import http.server, json, os, threading, time, urllib.request
TOK = os.environ['TOKEN']; W = '/w'; MAX = int(os.environ.get('MAX_SEC', '5400'))
def watchdog():
    time.sleep(MAX)
    try: urllib.request.urlopen(urllib.request.Request(f"https://rest.runpod.io/v1/pods/{os.environ.get('RUNPOD_POD_ID')}", method='DELETE', headers={'Authorization': 'Bearer ' + os.environ.get('RUNPOD_API_KEY', '')}), timeout=30)
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
            st = dict(stage=rd(W + '/stage').strip() or 'setup', files=files, log=rd(W + '/run.log', 3000),
                      setup=rd(W + '/setup.log', 2500), has_bundle=os.path.exists(W + '/bundle.tgz'))
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
mkdir -p /w/out /w/in; cd /w
echo "$SRV_PY_B64" | base64 -d > /w/srv.py; python3 /w/srv.py &
st() { echo "$1" > /w/stage; echo "[$(date +%H:%M:%S)] $1" >> /w/setup.log; }
export DEBIAN_FRONTEND=noninteractive
st apt
apt-get update -qq >>/w/setup.log 2>&1
apt-get install -y -qq --no-install-recommends git curl ca-certificates ffmpeg libgl1 libglib2.0-0 >>/w/setup.log 2>&1
nvidia-smi >>/w/setup.log 2>&1
st install_ltx
pip install -q uv >>/w/setup.log 2>&1
git clone --depth 1 https://github.com/Lightricks/LTX-2 /w/LTX-2 >>/w/setup.log 2>&1
cd /w/LTX-2 && uv sync --extra videoseal --extra audioseal >>/w/setup.log 2>&1 || { st install_failed; sleep infinity; }
st download_weights
T0=$(date +%s)
uv run python - >>/w/setup.log 2>&1 <<'PY' || { echo download_failed > /w/stage; }
import os
from huggingface_hub import hf_hub_download, snapshot_download
tok = os.environ.get('HF_TOKEN')
base = 'Lightricks/LTX-2.5'
for f in ['diffusion_models/ltx-2.5-22b-distilled-transformer-bf16.safetensors',
          'text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors',
          'vae/ltx-2.5-video-vae-bf16.safetensors', 'vae/ltx-2.5-audio-vae-bf16.safetensors',
          'latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors']:
    print('got', hf_hub_download(base, f, local_dir='/w/models', token=tok), flush=True)
print('got', hf_hub_download('Lightricks/LTX-2.5-22b-IC-LoRA-Layout-To-Render', 'ltx-2.5-22b-ic-lora-layout-to-render-1.0.safetensors', local_dir='/w/models/lora', token=tok), flush=True)
snapshot_download('Lightricks/LTX-2-Marking', local_dir='/w/marking', token=tok)
print('marking ok', flush=True)
PY
echo "download_seconds $(( $(date +%s) - T0 ))" >> /w/setup.log
du -sh /w/models /w/marking >> /w/setup.log 2>&1
[ "$(cat /w/stage)" = download_failed ] && sleep infinity
st wait_bundle
while [ ! -f /w/bundle.tgz ]; do sleep 2; done
tar xzf /w/bundle.tgz -C /w/in
st running
bash /w/in/run.sh >> /w/run.log 2>&1
st done
sleep infinity
'''


def api(method, path, body=None):
    req = urllib.request.Request(API + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + KEY, 'Content-Type': 'application/json', 'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            t = r.read()
            return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        raise SystemExit(f'RunPod API {method} {path} → {e.code}: {e.read().decode()[:600]}')


def pod_http(pid, token, method, path, data=None, timeout=90):
    req = urllib.request.Request(f'https://{pid}-8000.proxy.runpod.net{path}', method=method, data=data, headers={'X-Token': token, 'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def bundle(d):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as tf:
        for name in sorted(os.listdir(d)):
            tf.add(os.path.join(d, name), arcname=name)
    return buf.getvalue()


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    cmd = a[0]
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    if cmd == 'list':
        for p in api('GET', '/pods'):
            print(p.get('id'), p.get('name'), p.get('desiredStatus'), p.get('costPerHr'))
        return
    if cmd == 'kill-all':
        for p in api('GET', '/pods'):
            if str(p.get('name', '')).startswith(PREFIX):
                api('DELETE', f"/pods/{p['id']}")
                print('已删', p['id'])
        return
    in_dir, out_dir = a[1], a[2]
    max_h = float(opt('--max-hours', 1.5))
    if '--yes' not in a:
        raise SystemExit('要真的租卡，加 --yes')
    # --wait-for a,b,c：先开机（装环境、下权重和本机出素材同时进行），这些文件都到了输入目录才打包上传
    need = [x for x in (opt('--wait-for') or '').split(',') if x]
    def ready():
        return all(os.path.exists(os.path.join(in_dir, x)) for x in need)
    data = bundle(in_dir) if ready() else None
    if data is not None:
        print(f'输入包 {len(data) / 1e6:.1f} MB')
    else:
        print('输入还没齐，先开机，齐了再上传：', need, flush=True)
    os.makedirs(out_dir, exist_ok=True)
    token = secrets.token_urlsafe(24)
    body = dict(name=f'{PREFIX}0', imageName=IMAGE, gpuTypeIds=opt('--gpu', GPUS).split(','), gpuTypePriority='custom', gpuCount=1,
                cloudType='SECURE', containerDiskInGb=200, ports=['8000/http'], dockerEntrypoint=['bash', '-c'], dockerStartCmd=[POD_SH],
                env=dict(TOKEN=token, SRV_PY_B64=base64.b64encode(SRV_PY.encode()).decode(), MAX_SEC=str(int(max_h * 3600)),
                         HF_TOKEN='{{ RUNPOD_SECRET_hf_token }}', NVIDIA_DRIVER_CAPABILITIES='all'))
    if opt('--cuda'):
        body['allowedCudaVersions'] = opt('--cuda').split(',')
    p = api('POST', '/pods', body)
    pid = p['id']
    print(f"建好 pod {pid}  每小时 ${p.get('costPerHr')}  {(p.get('machine') or {}).get('gpuTypeId') or p.get('gpuTypeId') or '?'}", flush=True)
    t0, last, uploaded, got, done = time.time(), None, False, set(), False
    try:
        while not done:
            if time.time() - t0 > max_h * 3600:
                raise SystemExit('超过 --max-hours，停止')
            try:
                st = json.loads(pod_http(pid, token, 'GET', '/status', timeout=30))
            except Exception as e:
                st = dict(stage=f'连不上（{type(e).__name__}）', files=[])
            if st.get('has_bundle'):
                uploaded = True
            elif not uploaded and 'has_bundle' in st and (data is not None or ready()):
                if data is None:
                    time.sleep(3)                      # 等最后一个文件写完
                    data = bundle(in_dir)
                    print(f'输入包 {len(data) / 1e6:.1f} MB', flush=True)
                pod_http(pid, token, 'PUT', '/bundle', data, timeout=120)
                uploaded = True
                print('输入已上传', flush=True)
            for rel, size in st.get('files', []):
                dst = os.path.join(out_dir, rel)
                if rel in got or (os.path.exists(dst) and os.path.getsize(dst) == size):
                    got.add(rel)
                    continue
                try:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    open(dst, 'wb').write(pod_http(pid, token, 'GET', '/out/' + rel, timeout=300))
                    got.add(rel)
                except Exception as e:
                    print('下载失败，下轮重试', rel, e)
            msg = f"[{(time.time() - t0) / 60:5.1f} 分] {st.get('stage')} 已拉回 {len(got)}"
            if msg != last:
                print(msg, flush=True)
                last = msg
            stage = str(st.get('stage'))
            if stage in ('done', 'install_failed', 'download_failed'):
                open(os.path.join(out_dir, 'pod_setup.log'), 'w').write(st.get('setup', ''))
                open(os.path.join(out_dir, 'pod_run.log'), 'w').write(st.get('log', ''))
                if stage == 'done':
                    st2 = json.loads(pod_http(pid, token, 'GET', '/status', timeout=30))
                    if all(f[0] in got for f in st2.get('files', [])):
                        done = True
                else:
                    print('pod 上失败：', stage)
                    done = True
            time.sleep(20)
        print(f"完成：墙钟 {(time.time() - t0) / 60:.1f} 分钟，约 ${(p.get('costPerHr') or 0) * (time.time() - t0) / 3600:.2f}（上限估计，以账单为准）")
    finally:
        if '--keep' not in a:
            try:
                api('DELETE', f'/pods/{pid}')
                print('已删除 pod', pid)
            except SystemExit as e:
                print('删除失败，请运行 kill-all：', e)


if __name__ == '__main__':
    main()
