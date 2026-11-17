#!/usr/bin/env python3
"""Same as experiments/ltx_poc04/runpod_ltx.py, but the three RunPod control calls (create / list / delete pod) go
through RunPod's GraphQL API (api.runpod.io) instead of the REST API (rest.runpod.io).

Why: from this cloud container rest.runpod.io returned 502 "upstream request failed" for >2 hours on 2026-11-17
(also for the public /openapi.json, also after re-saving and replacing the key), while api.runpod.io answered and the
RunPod console worked. The API key is injected by the session proxy for api.runpod.io (Authorization: Bearer).

Everything else (pod startup script, in-pod HTTP server, upload / download over <pod>-8000.proxy.runpod.net,
--max-hours watchdog, delete on exit) is the original code. The in-pod watchdog additionally tries GraphQL
podTerminate if its REST DELETE fails.

  python3 runpod_ltx_gql.py run <in dir> <out dir> [--gpu "id1,id2"] [--max-hours h] --yes
  python3 runpod_ltx_gql.py list | kill-all
"""
import base64
import importlib.util
import json
import os
import shlex
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('runpod_ltx', os.path.join(HERE, '..', 'ltx_poc04', 'runpod_ltx.py'))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

GQL = 'https://api.runpod.io/graphql'


def gql(query, variables=None):
    req = urllib.request.Request(GQL, method='POST', data=json.dumps(dict(query=query, variables=variables or {})).encode(),
                                 headers={'Authorization': 'Bearer ' + R.KEY, 'Content-Type': 'application/json',
                                          'User-Agent': R.UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f'RunPod GraphQL → {e.code}: {e.read().decode()[:600]}')
    if out.get('errors'):
        raise RuntimeError(json.dumps(out['errors'])[:800])
    return out['data']


def api(method, path, body=None):
    if method == 'GET' and path == '/pods':
        return gql('query { myself { pods { id name desiredStatus costPerHr } } }')['myself']['pods']
    if method == 'DELETE' and path.startswith('/pods/'):
        gql('mutation($i: PodTerminateInput!) { podTerminate(input: $i) }', dict(i=dict(podId=path.split('/')[-1])))
        return {}
    if method == 'POST' and path == '/pods':
        # REST used entrypoint ["bash","-c"] + startCmd [POD_SH]; GraphQL takes one command string, so the script
        # travels base64-encoded in an env var and the command only decodes and runs it.
        env = dict(body['env'], POD_SH_B64=base64.b64encode(body['dockerStartCmd'][0].encode()).decode())
        base = dict(name=body['name'], imageName=body['imageName'], cloudType=body['cloudType'], gpuCount=1,
                    containerDiskInGb=body['containerDiskInGb'], volumeInGb=0, ports=','.join(body['ports']),
                    dockerArgs="bash -c 'echo $POD_SH_B64 | base64 -d > /pod.sh && bash /pod.sh'",
                    env=[dict(key=k, value=v) for k, v in env.items()])
        last = None
        for gpu in body['gpuTypeIds']:
            try:
                p = gql('mutation($i: PodFindAndDeployOnDemandInput) { podFindAndDeployOnDemand(input: $i) '
                        '{ id costPerHr machine { gpuDisplayName } } }', dict(i=dict(base, gpuTypeId=gpu)))
                p = p['podFindAndDeployOnDemand']
                p['gpuTypeId'] = gpu
                return p
            except RuntimeError as e:
                last = e
                print(f'{gpu}: {e}'[:300], flush=True)
        raise SystemExit(f'no GPU available: {last}')
    raise SystemExit(f'unsupported call {method} {path}')


R.api = api
# in-pod watchdog: after the REST DELETE attempt, also try GraphQL podTerminate (rest.runpod.io may be unreachable)
old = "    except Exception as e: open(W + '/watchdog.log', 'a').write(repr(e) + '\\n')\n    os._exit(0)"
assert old in R.SRV_PY, 'watchdog block not found'
R.SRV_PY = R.SRV_PY.replace(old, """    except Exception as e: open(W + '/watchdog.log', 'a').write(repr(e) + '\\n')
    try:
        q = json.dumps(dict(query='mutation { podTerminate(input: {podId: "%s"}) }' % os.environ.get('RUNPOD_POD_ID')))
        urllib.request.urlopen(urllib.request.Request('https://api.runpod.io/graphql', method='POST', data=q.encode(),
            headers={'Authorization': 'Bearer ' + os.environ.get('RUNPOD_API_KEY', ''), 'Content-Type': 'application/json'}), timeout=30)
    except Exception as e: open(W + '/watchdog.log', 'a').write(repr(e) + '\\n')
    os._exit(0)""")

if __name__ == '__main__':
    sys.argv[0] = 'runpod_ltx_gql.py'
    R.main()
