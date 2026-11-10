# 把 PNG 序列编码成 MP4（H.264，高质量），用 Blender 自带的视频编码，Windows 上不用另装 ffmpeg。
# 用法：blender -b --python-exit-code 1 --python encode_mp4.py -- <帧目录> <输出 mp4> <fps>
import bpy, sys, os
args = sys.argv[sys.argv.index('--') + 1:]; FR, OUT, FPS = args[0], args[1], int(args[2]); NEED = int(args[3]) if len(args) > 3 else 0
files = sorted(f for f in os.listdir(FR) if f.lower().endswith('.png'))
if not files: raise SystemExit('帧目录里没有 PNG：' + FR)
if NEED:                                              # 编码前核对：帧要齐、要连续、不能有坏文件（审核 11-10 第 4 条）
    bad = [n for n in range(1, NEED + 1) if not os.path.exists(os.path.join(FR, f'f{n:04d}.png')) or os.path.getsize(os.path.join(FR, f'f{n:04d}.png')) < 10000]
    if bad:
        print('[!] 有', len(bad), '帧缺失或不完整，例如：', ['f%04d.png' % n for n in bad[:10]], '。请再双击 start_render_eevee.bat 补渲。')
        sys.exit(1)
    files = [f'f{n:04d}.png' for n in range(1, NEED + 1)]
sc = bpy.context.scene
if sc.sequence_editor is None: sc.sequence_editor_create()
ed = sc.sequence_editor
strips = ed.strips if hasattr(ed, 'strips') else ed.sequences          # 新版 Blender 把 sequences 改名为 strips
st = strips.new_image('frames', os.path.join(FR, files[0]), channel=1, frame_start=1)
for f in files[1:]: st.elements.append(f)
im = bpy.data.images.load(os.path.join(FR, files[0])); w, h = im.size
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = w, h, 100
sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, len(files)
sc.view_settings.view_transform = 'Standard'                          # 帧已经是调好色的成品，编码时不再套色彩变换
ims = sc.render.image_settings
if hasattr(ims, 'media_type'): ims.media_type = 'VIDEO'
ims.file_format = 'FFMPEG'; sc.render.ffmpeg.format = 'MPEG4'; sc.render.ffmpeg.codec = 'H264'
for k, v in (('constant_rate_factor', 'HIGH'), ('ffmpeg_preset', 'GOOD')):   # 高质量但文件不至于上百 MB，方便发回
    try: setattr(sc.render.ffmpeg, k, v)
    except Exception as e: print('编码设置跳过', k, e)
sc.render.filepath = OUT; sc.render.use_file_extension = False
bpy.ops.render.render(animation=True)
print('ENCODED', OUT, len(files), '帧')
