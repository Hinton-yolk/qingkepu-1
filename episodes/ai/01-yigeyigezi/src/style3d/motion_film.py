# EP.01 运动草稿合成：3D 帧 → 2D 层（字幕、标签）→ 拍与拍之间的转场 → 编码 + 配乐。
# 用法：FILM_THEME=desk python3 motion_film.py <3D 帧目录> <工作目录> <music.wav> <fps>
# 转场（草稿）：每拍开头 0.4 秒，上一拍最后一帧边轻轻放大边淡出，新的一拍从底下出来；同章节的拍之间更短（0.25 秒）。
import sys, os, glob, json, subprocess
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from film_overlay import compose

src, work, music, fps = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
comp = os.path.join(work, 'comp'); os.makedirs(comp, exist_ok=True)
frames = sorted(glob.glob(os.path.join(src, 'f*.png')))
meta = [json.load(open(p[:-4] + '.json')) for p in frames]
# 先并行叠 2D 层（每帧独立），再按顺序做转场
from multiprocessing import Pool
def _one(p):
    o = os.path.join(work, 'ov', os.path.basename(p))
    if not os.path.exists(o): compose(p, p[:-4] + '.json').save(o)
    return o
os.makedirs(os.path.join(work, 'ov'), exist_ok=True)
with Pool(4) as pool: ovs = pool.map(_one, frames, chunksize=8)
prev_last = None; prev_beat = None; beat_start = 0; last_img = None
for i, (p, m) in enumerate(zip(frames, meta)):
    im = Image.open(ovs[i]).convert('RGB')
    b = m['beat']
    if b != prev_beat:
        prev_last = last_img; beat_start = i; prev_beat = b
    dt = (i - beat_start) / fps
    D = 0.4
    if prev_last is not None and dt < D:
        a = 1 - dt / D                                     # 上一拍的残影：慢慢放大、淡出
        s = 1.0 + 0.05 * (1 - a)
        w, h = prev_last.size
        z = prev_last.resize((int(w * s), int(h * s)), Image.LANCZOS)
        z = z.crop(((z.width - w) // 2, (z.height - h) // 2, (z.width - w) // 2 + w, (z.height - h) // 2 + h))
        im = Image.blend(im, z, a * a)
    im.save(os.path.join(comp, f'f{i:05d}.jpg'), quality=92)
    last_img = im.copy()
n = len(frames)
vid = os.path.join(work, 'video_silent.mp4')
subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-framerate', str(fps), '-i', os.path.join(comp, 'f%05d.jpg'),
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', vid], check=True)
# 响度两遍 loudnorm 到 -14 LUFS，真峰值 ≤ -1.5 dBTP
r = subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-i', music, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True)
j = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
out = os.path.join(work, 'EP01_运动草稿.mp4')
# 草稿 12 帧 / 秒：混合插帧到 30 帧，播放更顺；动效检查也按 30 帧量（tools/motion_check.py 统一重采样到 30 帧）
subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-i', vid, '-i', music, '-af', af, '-vf', 'minterpolate=fps=30:mi_mode=blend',
                '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out], check=True)
print('ok', n, 'frames ->', out)
