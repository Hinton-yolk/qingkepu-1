#!/usr/bin/env python3
"""生成 PR 里「视频审核交付」一节要用的表格：文件大小、sha256、时长、宽高、帧率、帧数、音轨、对应提交。
用法：python3 tools/preview_manifest.py <视频文件> --commit <生成这段视频时的代码提交> [--url 直链] [--note 说明] [--row 键=值 …]
  --commit 必填：写视频实际生成所依据的提交，不要填交付时的分支最新提交。
  --row 可以重复，用来加「压缩方式」「原始文件」「共享权限」这类行。
不上传任何东西，只读本地文件。依赖 ffprobe。"""
import argparse, hashlib, json, os, subprocess, sys, time

def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                          'stream=codec_type,codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels:format=duration,size',
                          '-of', 'json', path], capture_output=True, text=True, check=True).stdout
    return json.loads(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video'); ap.add_argument('--url', default='（还没有可用的直链）')
    ap.add_argument('--commit', required=True); ap.add_argument('--note', default='')
    ap.add_argument('--row', action='append', default=[], metavar='键=值')
    a = ap.parse_args()
    h = hashlib.sha256()
    with open(a.video, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
    info = probe(a.video); fmt = info['format']
    v = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    au = next((s for s in info['streams'] if s['codec_type'] == 'audio'), None)
    if v is None: sys.exit('没有视频流：' + a.video)
    num, den = (int(x) for x in v['r_frame_rate'].split('/')); fps = num / den
    full = subprocess.run(['git', 'rev-parse', '--verify', '-q', a.commit + '^{commit}'], capture_output=True, text=True).stdout.strip()
    commit = full or a.commit
    size = int(fmt['size'])
    rows = [
        ('文件名', '`' + os.path.basename(a.video) + '`'),
        ('直接下载地址', a.url),
        ('生成时依据的代码提交', '`' + commit + '`'),
        ('时长', f"{float(fmt['duration']):.2f} 秒"),
        ('宽 × 高', f"{v['width']} × {v['height']}"),
        ('帧率 / 帧数', f"{fps:g} fps / {v.get('nb_frames', '?')} 帧"),
        ('视频编码', v['codec_name']),
        ('音轨', f"{au['codec_name']}，{au.get('sample_rate', '?')} Hz，{au.get('channels', '?')} 声道" if au else '无（无声）'),
        ('文件大小', f"{size:,} 字节（{size / 1048576:.2f} MB）".replace(',', ' ')),
        ('sha256', '`' + h.hexdigest() + '`'),
        ('文件修改时间', time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(os.path.getmtime(a.video)))),
    ]
    for r in a.row:
        k, _, val = r.partition('='); rows.append((k.strip(), val.strip()))
    if a.note: rows.append(('说明', a.note))
    print('| 项 | 值 |\n|---|---|')
    for k, val in rows: print(f'| {k} | {val} |')

if __name__ == '__main__':
    main()
