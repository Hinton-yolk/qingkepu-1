#!/usr/bin/env python3
"""tools/runpod_render.py（Cycles 云渲染），但建机 / 列表 / 删机走 RunPod GraphQL（api.runpod.io）。

原因：2026-11-17 起本云容器到 rest.runpod.io 持续 502 "upstream request failed"，api.runpod.io 可用
（同样的做法见 experiments/lightpath_s04_v2/runpod_ltx_gql.py，分支 claude/optimistic-faraday-7ux180）。
其余（pod 启动脚本、pod 内 HTTP 服务、上传下载走 <pod>-8000.proxy.runpod.net、看门狗、退出时删机）沿用原脚本。

  python3 tools/runpod_render_gql.py plan|run <jobs.json> [--pods N] [--gpu "id1,id2"] [--max-hours h] [--yes]
  python3 tools/runpod_render_gql.py list | kill-all
"""
import base64, importlib.util, json, os, sys, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('runpod_render', os.path.join(HERE, 'runpod_render.py'))
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
GQL = 'https://api.runpod.io/graphql'

def gql(query, variables=None):
    req = urllib.request.Request(GQL, method='POST', data=json.dumps(dict(query=query, variables=variables or {})).encode(),
                                 headers={'Authorization': 'Bearer ' + R.KEY, 'Content-Type': 'application/json', 'User-Agent': R.UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: out = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f'RunPod GraphQL → {e.code}: {e.read().decode()[:600]}')
    if out.get('errors'): raise RuntimeError(json.dumps(out['errors'])[:800])
    return out['data']

def api(method, path, body=None):
    if method == 'GET' and path == '/pods':
        return gql('query { myself { pods { id name desiredStatus costPerHr } } }')['myself']['pods']
    if method == 'DELETE' and path.startswith('/pods/'):
        gql('mutation($i: PodTerminateInput!) { podTerminate(input: $i) }', dict(i=dict(podId=path.split('/')[-1]))); return {}
    if method == 'POST' and path == '/pods':
        env = dict(body['env'], POD_SH_B64=base64.b64encode(body['dockerStartCmd'][0].encode()).decode())
        base = dict(name=body['name'], imageName=body['imageName'], cloudType=body['cloudType'], gpuCount=1,
                    containerDiskInGb=body['containerDiskInGb'], volumeInGb=0, ports=','.join(body['ports']),
                    dockerArgs="bash -c 'echo $POD_SH_B64 | base64 -d > /pod.sh && bash /pod.sh'",
                    env=[dict(key=k, value=v) for k, v in env.items()])
        last = None
        for gpu in body['gpuTypeIds']:
            try:
                p = gql('mutation($i: PodFindAndDeployOnDemandInput) { podFindAndDeployOnDemand(input: $i) '
                        '{ id costPerHr machine { gpuDisplayName } } }', dict(i=dict(base, gpuTypeId=gpu)))['podFindAndDeployOnDemand']
                p['gpuTypeId'] = gpu; return p
            except RuntimeError as e:
                last = e; print(f'{gpu}: {e}'[:300], flush=True)
        raise SystemExit(f'no instances available: {last}')
    raise SystemExit(f'unsupported call {method} {path}')

R.api = api
old = "        except Exception as e: open(W + '/watchdog.log', 'a').write(repr(e) + '\\n')\n    os._exit(0)"
assert old in R.SRV_PY, 'watchdog block not found'
R.SRV_PY = R.SRV_PY.replace(old, """        except Exception as e: open(W + '/watchdog.log', 'a').write(repr(e) + '\\n')
    try:
        q = json.dumps(dict(query='mutation { podTerminate(input: {podId: "%s"}) }' % os.environ.get('RUNPOD_POD_ID')))
        urllib.request.urlopen(urllib.request.Request('https://api.runpod.io/graphql', method='POST', data=q.encode(),
            headers={'Authorization': 'Bearer ' + os.environ.get('RUNPOD_API_KEY', ''), 'Content-Type': 'application/json'}), timeout=30)
    except Exception as e: open(W + '/watchdog.log', 'a').write(repr(e) + '\\n')
    os._exit(0)""")

if __name__ == '__main__':
    sys.argv[0] = 'runpod_render_gql.py'; R.main()
