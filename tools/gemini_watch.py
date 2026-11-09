#!/usr/bin/env python3
"""Ask Gemini about a video, streaming the answer.

Why this exists: in the cloud sessions every outbound request goes through a proxy that drops a
request after ~30 s without a response byte. Gemini often needs longer than that to watch a whole
video, so a normal (non-streaming) generateContent call fails with "HTTP 502: upstream request
failed". With streamGenerateContent the first bytes usually arrive in time. When a model is busy
(503), too slow (502 at ~30 s) or unavailable to the key (404), the next model in the list is tried.

usage:
  python3 tools/gemini_watch.py <YouTube URL | local video file> -q "问题"
         [--models m1,m2,...] [--start 1:00] [--end 2:30] [--out answer.md]

- YouTube URLs are passed to Google directly; nothing is downloaded here.
- A local file is uploaded to the Gemini Files API, used once, then deleted.
- The key is read from GEMINI_API_KEY, then ~/.config/watch/.env. In the cloud environment the
  proxy injects the real key into the x-goog-api-key header, so a placeholder value is enough there.
- The answer is Gemini's account of the video, not a verified fact. Standard library only.
"""
import argparse
import json
import mimetypes
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API = 'https://generativelanguage.googleapis.com'
DEFAULT_MODELS = ['gemini-3.5-flash', 'gemini-3.6-flash', 'gemini-3.7-flash', 'gemini-flash-latest']
RETRY_NEXT = {404, 429, 500, 502, 503, 504}
YOUTUBE = re.compile(r'^https?://(www\.|m\.)?(youtube\.com|youtu\.be)/', re.I)


def api_key() -> str:
    key = os.environ.get('GEMINI_API_KEY', '').strip()
    if key:
        return key
    cfg = Path.home() / '.config' / 'watch' / '.env'
    if cfg.exists():
        for line in cfg.read_text(encoding='utf-8-sig').splitlines():
            m = re.match(r'\s*GEMINI_API_KEY\s*=\s*"?([^"\s]*)"?\s*$', line)
            if m and m.group(1):
                key = m.group(1)
    if not key and Path('/root/.ccr/ca-bundle.crt').exists():
        # Claude Code cloud session: the real key is a network secret the proxy injects into
        # x-goog-api-key, so the header only needs to be present.
        print('[gemini_watch] no local key; using a placeholder, the cloud proxy injects the real one',
              file=sys.stderr)
        key = 'proxy-injected-placeholder'
    if not key:
        sys.exit('No GEMINI_API_KEY found (environment or ~/.config/watch/.env).')
    return key


def seconds(t: str) -> str:
    parts = [float(p) for p in t.split(':')]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return f'{total:g}s'


def call(method, url, key, data=None, headers=None, timeout=120):
    req = Request(url, data=data, method=method, headers={'x-goog-api-key': key, **(headers or {})})
    return urlopen(req, timeout=timeout)


def error_text(e: HTTPError) -> str:
    try:
        body = e.read().decode('utf-8', 'replace')
        msg = json.loads(body).get('error', {}).get('message', body)
    except Exception:
        msg = str(e)
    return f'HTTP {e.code}: {msg.strip()[:200]}'


def upload(path: Path, key: str) -> dict:
    size = path.stat().st_size
    mime = mimetypes.guess_type(path.name)[0] or 'video/mp4'
    with call('POST', f'{API}/upload/v1beta/files', key,
              data=json.dumps({'file': {'display_name': path.name}}).encode(),
              headers={'X-Goog-Upload-Protocol': 'resumable', 'X-Goog-Upload-Command': 'start',
                       'X-Goog-Upload-Header-Content-Length': str(size),
                       'X-Goog-Upload-Header-Content-Type': mime,
                       'Content-Type': 'application/json'}) as r:
        session = r.headers.get('x-goog-upload-url')
    if not session:
        sys.exit('Upload failed: no upload session URL returned.')
    print(f'[gemini_watch] uploading {path.name} ({size / 1e6:.1f} MB)…', file=sys.stderr)
    with call('POST', session, key, data=path.read_bytes(), timeout=900,
              headers={'Content-Length': str(size), 'X-Goog-Upload-Offset': '0',
                       'X-Goog-Upload-Command': 'upload, finalize'}) as r:
        info = json.loads(r.read())['file']
    deadline = time.time() + 900
    while info.get('state') == 'PROCESSING':
        if time.time() > deadline:
            sys.exit('Gemini is still processing the upload after 15 minutes.')
        time.sleep(3)
        with call('GET', f"{API}/v1beta/{info['name']}", key) as r:
            info = json.loads(r.read())
    if info.get('state') != 'ACTIVE':
        sys.exit(f"Upload ended in state {info.get('state')}.")
    return info


def delete(info: dict, key: str) -> None:
    try:
        call('DELETE', f"{API}/v1beta/{info['name']}", key, timeout=30).close()
    except Exception as e:  # an undeleted upload expires within 48 hours anyway
        print(f'[gemini_watch] could not delete {info["name"]}: {e}', file=sys.stderr)


def stream(model, body, key, sink):
    """Stream one answer; return (ok, error_message). Text is written to sink as it arrives."""
    url = f'{API}/v1beta/models/{model}:streamGenerateContent?alt=sse'
    try:
        with call('POST', url, key, data=json.dumps(body).encode(),
                  headers={'Content-Type': 'application/json'}, timeout=300) as r:
            got = False
            for raw in r:
                line = raw.decode('utf-8', 'replace').strip()
                if not line.startswith('data:'):
                    continue
                chunk = json.loads(line[5:])
                for cand in chunk.get('candidates', []):
                    for part in cand.get('content', {}).get('parts', []):
                        if part.get('text') and not part.get('thought'):
                            sink(part['text'])
                            got = True
            return (True, None) if got else (False, 'empty answer')
    except HTTPError as e:
        return False, error_text(e)
    except (URLError, TimeoutError, ConnectionError) as e:
        return False, f'network: {e}'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('source', help='YouTube URL or local video file')
    ap.add_argument('-q', '--question', required=True)
    ap.add_argument('--models', default=os.environ.get('WATCH_GEMINI_MODELS', ','.join(DEFAULT_MODELS)),
                    help='comma-separated, tried in order')
    ap.add_argument('--start', help='SS, MM:SS or HH:MM:SS')
    ap.add_argument('--end', help='SS, MM:SS or HH:MM:SS')
    ap.add_argument('--out', help='also write the answer to this Markdown file')
    a = ap.parse_args()

    key = api_key()
    uploaded = None
    if YOUTUBE.match(a.source):
        video = {'file_data': {'file_uri': a.source}}
        where = f'{a.source} (URL sent to Google)'
    else:
        path = Path(a.source).expanduser()
        if not path.is_file():
            sys.exit(f'Not a YouTube URL or an existing file: {a.source}')
        uploaded = upload(path, key)
        video = {'file_data': {'file_uri': uploaded['uri'], 'mime_type': uploaded.get('mimeType', 'video/mp4')}}
        where = f'{path} (uploaded to the Gemini Files API, deleted afterwards)'
    if a.start or a.end:
        video['video_metadata'] = {k: v for k, v in
                                   (('start_offset', a.start and seconds(a.start)),
                                    ('end_offset', a.end and seconds(a.end))) if v}
    body = {'contents': [{'parts': [video, {'text': a.question}]}]}

    answer, used, errors = [], None, []
    try:
        for model in [m.strip() for m in a.models.split(',') if m.strip()]:
            print(f'[gemini_watch] asking {model}…', file=sys.stderr)
            parts = []
            ok, err = stream(model, body, key, lambda t: (parts.append(t), print(t, end='', flush=True)))
            if ok:
                answer, used = parts, model
                print(flush=True)
                break
            errors.append(f'{model}: {err}')
            print(f'[gemini_watch] {model} failed: {err}', file=sys.stderr)
            code = re.match(r'HTTP (\d+)', err or '')
            if code and int(code.group(1)) not in RETRY_NEXT and 'model' not in (err or '').lower():
                break
    finally:
        if uploaded:
            delete(uploaded, key)

    if not used:
        sys.exit('No model answered:\n  ' + '\n  '.join(errors))
    if a.out:
        Path(a.out).write_text(
            f'# Gemini 看视频\n\n- 来源：{where}\n- 模型：{used}\n- 问题：{a.question}\n'
            f'- 时间：{time.strftime("%Y-%m-%d %H:%M")}\n\n'
            f'> 以下是 Gemini 看完视频后的描述，不是核实过的事实。\n\n{"".join(answer).strip()}\n',
            encoding='utf-8')
        print(f'[gemini_watch] saved to {a.out}', file=sys.stderr)


if __name__ == '__main__':
    main()
