#!/usr/bin/env python3
"""在 RunPod 上用 GPU 渲 three.js 草稿（无头 Chromium + 该集的 render.mjs），渲完在 pod 上编码，只拉回 mp4。

  python3 tools/runpod_chromium.py run --root episodes/ai-linghun/01-strawberry \
      --out episodes/ai-linghun/01-strawberry/film/out/ai01-strawberry-film-draft-v2.mp4 [--gpu "id1,id2"] [--max-hours 1.5] [--yes]
  python3 tools/runpod_chromium.py list | kill-all

流程：建一台 GPU pod（镜像 mcr.microsoft.com/playwright，带 Chromium 和 node）→ 上传 film/、timeline.js、assets/、three →
  先试几种让 Chromium 用上显卡的参数（tools/runpod_chromium_probe.mjs，各渲 12 张），挑最快的 → 渲整片 → ffmpeg 编码 →
  拉回 mp4 和试渲截图（<out 所在目录>/runpod/）→ 删 pod。
建机 / 删机走 GraphQL（同 tools/runpod_render_gql.py）；pod 内 HTTP 服务、看门狗沿用 tools/runpod_render.py。
API key 由网络代理注入，这里不存；本脚本退出（包括出错、Ctrl-C）时删掉自己建的 pod，除非 --keep。
"""
import base64, importlib.util, io, json, os, secrets, sys, tarfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('runpod_render_gql', os.path.join(HERE, 'runpod_render_gql.py'))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
R = G.R
REPO = R.REPO
PW = '1.63.0'                                   # 和本机 Playwright 同版本，镜像里的浏览器版本才对得上
IMAGE = f'mcr.microsoft.com/playwright:v{PW}-noble'
GPUS = 'NVIDIA GeForce RTX 4090,NVIDIA GeForce RTX 3090,NVIDIA RTX A5000,NVIDIA RTX A4000,NVIDIA L4,NVIDIA RTX 4000 Ada Generation'
INCLUDE = ['film/index.html', 'film/render.mjs', 'timeline.js', 'assets',
           'v4-3d/node_modules/three/package.json', 'v4-3d/node_modules/three/build', 'v4-3d/node_modules/three/examples/jsm']

POD_SH = r'''
mkdir -p /w/out; cd /w; export DEBIAN_FRONTEND=noninteractive
echo apt > /w/stage
apt-get update -qq >>/w/setup.log 2>&1
command -v python3 >/dev/null || apt-get install -y -qq python3 >>/w/setup.log 2>&1
echo "$SRV_PY_B64" | base64 -d > /w/srv.py; python3 /w/srv.py &
apt-get install -y -qq --no-install-recommends ffmpeg libegl1 libgles2 libgl1 libvulkan1 vulkan-tools >>/w/setup.log 2>&1
echo npm > /w/stage
npm i -g playwright@$PW >>/w/setup.log 2>&1
export NODE_PATH=$(npm root -g)
{ nproc; nvidia-smi; vulkaninfo --summary; ls /usr/share/glvnd/egl_vendor.d /etc/vulkan/icd.d /usr/share/vulkan/icd.d /ms-playwright; } >>/w/setup.log 2>&1
echo wait_bundle > /w/stage
while [ ! -f /w/bundle.tgz ]; do sleep 2; done
mkdir -p /w/scene && tar xzf /w/bundle.tgz -C /w/scene
echo probe > /w/stage
if node /w/scene/_probe.mjs /w/scene/film >> /w/render.log 2>&1; then
  . /w/chosen.env
  echo rendering > /w/stage
  cd /w/scene/film
  if node render.mjs --workers=$WORKERS --out=out/film.mp4 >> /w/render.log 2>&1; then mv out/film.mp4 /w/out/film.mp4; else echo "render failed" >> /w/fails; fi
else echo "probe failed: no Chromium config worked" >> /w/fails; fi
echo done > /w/stage
sleep infinity
'''


def bundle(root):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz') as tf:
        for rel in INCLUDE: tf.add(os.path.join(root, rel), arcname=rel)
        tf.add(os.path.join(HERE, 'runpod_chromium_probe.mjs'), arcname='_probe.mjs')
    return buf.getvalue()


MUT = 'mutation($i: PodFindAndDeployOnDemandInput) { podFindAndDeployOnDemand(input: $i) { id costPerHr machine { gpuDisplayName } } }'


def create(env, gpus, cloud):
    base = dict(name=f'{R.PREFIX}chromium', imageName=IMAGE, cloudType=cloud, gpuCount=1, containerDiskInGb=40, volumeInGb=0,
                ports='8000/http', minVcpuCount=8, minMemoryInGb=24,
                dockerArgs="bash -c 'echo $POD_SH_B64 | base64 -d > /pod.sh && bash /pod.sh'",
                env=[dict(key=k, value=v) for k, v in env.items()])
    for gpu in gpus:
        try:
            p = G.gql(MUT, dict(i=dict(base, gpuTypeId=gpu)))['podFindAndDeployOnDemand']
            if p: p['gpu'] = gpu; return p
        except RuntimeError as e:
            print(f'{gpu}: {e}'[:300], flush=True)
    return None


def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return
    cmd = a[0]; opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    if cmd in ('list', 'kill-all'):
        for p in G.api('GET', '/pods'):
            if cmd == 'list': print(p.get('id'), p.get('name'), p.get('desiredStatus'), p.get('costPerHr'))
            elif str(p.get('name', '')).startswith(R.PREFIX): G.api('DELETE', f"/pods/{p['id']}"); print('已删', p['id'], p.get('name'))
        return
    root = os.path.join(REPO, opt('--root')); out = os.path.join(REPO, opt('--out'))
    max_h = float(opt('--max-hours', 1.5)); gpus = opt('--gpu', GPUS).split(',')
    data = bundle(root); print(f'场景包 {len(data) / 1e6:.1f} MB')
    if '--yes' not in a: raise SystemExit('要真的租卡，加 --yes')
    token = secrets.token_urlsafe(24)
    env = dict(TOKEN=token, SRV_PY_B64=base64.b64encode(R.SRV_PY.encode()).decode(), POD_SH_B64=base64.b64encode(POD_SH.encode()).decode(),
               PW=PW, MAX_SEC=str(int(max_h * 3600)), NVIDIA_DRIVER_CAPABILITIES='all')
    pod = None
    try:
        for cloud in ('COMMUNITY', 'SECURE'):
            pod = create(env, gpus, cloud)
            if pod: break
            print(f'{cloud} 没有空卡')
        if not pod: raise SystemExit('没租到卡')
        pid = pod['id']; print(f"建好 pod {pid}：{pod.get('gpu')}，每小时 ${pod.get('costPerHr')}", flush=True)
        os.makedirs(os.path.dirname(R.STATE), exist_ok=True); json.dump([dict(id=pid, token=token)], open(R.STATE, 'w'))
        t0 = time.time(); last = None; up = False
        while True:
            if time.time() - t0 > max_h * 3600: raise SystemExit('超过 --max-hours，停止')
            try: st = json.loads(R.pod_http(pid, token, 'GET', '/status', timeout=30))
            except Exception as e: st = dict(stage=f'连不上（{type(e).__name__}，pod 可能还在启动）', files=[])
            if st.get('has_bundle'): up = True
            elif not up and 'has_bundle' in st:
                R.pod_http(pid, token, 'PUT', '/bundle', data, timeout=95); up = True; print('场景已上传', flush=True)
            tail = [l for l in (st.get('log') or '').splitlines() if l.strip()][-1:]
            msg = f"{st.get('stage')} {tail[0].strip()[:160] if tail else ''}"
            if msg != last: print(f'[{(time.time() - t0) / 60:5.1f} 分] {msg}', flush=True); last = msg
            if st.get('stage') == 'done':
                rd = os.path.join(os.path.dirname(out), 'runpod'); os.makedirs(rd, exist_ok=True)
                for rel, size in st.get('files', []):
                    dst = out if rel == 'film.mp4' else os.path.join(rd, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    open(dst, 'wb').write(R.pod_http(pid, token, 'GET', '/out/' + rel, timeout=300)); print('拉回', rel, f'{size / 1e6:.1f} MB')
                open(os.path.join(rd, 'log.txt'), 'w').write((st.get('log') or '') + '\n---setup---\n' + (st.get('setup') or ''))
                if st.get('fails'): print('失败：', st['fails'])
                break
            time.sleep(15)
        mins = (time.time() - t0) / 60
        print(f"完成：{mins:.1f} 分钟，约 ${(pod.get('costPerHr') or 0) * mins / 60:.2f}（按秒计费，以 RunPod 账单为准）")
    finally:
        if pod and '--keep' not in a:
            try: G.api('DELETE', f"/pods/{pod['id']}"); print('已删除 pod', pod['id'])
            except BaseException as e: print('删除失败，请运行 kill-all：', e)


if __name__ == '__main__':
    main()
