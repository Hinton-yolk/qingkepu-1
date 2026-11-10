# 把 PNG 序列编码成 MP4（H.264，高质量），用 Blender 自带的视频编码，Windows 上不用另装 ffmpeg。
# 用法：blender -b --python-exit-code 1 --python encode_mp4.py -- <帧目录> <输出 mp4> <fps>
import bpy, sys, os
args = sys.argv[sys.argv.index('--') + 1:]; FR, OUT, FPS = args[0], args[1], int(args[2])
files = sorted(f for f in os.listdir(FR) if f.lower().endswith('.png'))
if not files: raise SystemExit('帧目录里没有 PNG：' + FR)
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
for k, v in (('constant_rate_factor', 'PERC_LOSSLESS'), ('ffmpeg_preset', 'GOOD')):
    try: setattr(sc.render.ffmpeg, k, v)
    except Exception as e: print('编码设置跳过', k, e)
sc.render.filepath = OUT; sc.render.use_file_extension = False
bpy.ops.render.render(animation=True)
print('ENCODED', OUT, len(files), '帧')
