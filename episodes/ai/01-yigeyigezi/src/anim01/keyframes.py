# 整理交付目录：视频、轨迹图 / 数据、关键构图帧（从合成好的 1080×1920 帧里取）
import os, shutil, sys
KEY = {'a': ('AnimationTest_A_Branch', [0.3, 2.8, 4.4, 7.0, 9.8, 11.4, 13.8]),
       'b': ('AnimationTest_B_ModelFlow', [0.3, 1.6, 2.6, 4.3, 6.2, 8.5, 9.4, 10.4]),
       'c': ('AnimationTest_C_SpeculativeDecoding', [1.4, 2.8, 5.6, 7.4, 8.8, 10.4, 11.3, 15.0])}
src, dst = 'out/post', 'out/deliver'
for s in sys.argv[1:]:
    name, ts = KEY[s]; os.makedirs(os.path.join(dst, f'{s}_关键帧'), exist_ok=True)
    for ext in ('.mp4', '_轨迹.jpg', '_轨迹.json'): shutil.copy(os.path.join(src, name + ext), os.path.join(dst, name + ext))
    for t in ts:
        fi = int(round(t * 30)); shutil.copy(os.path.join(src, f'comp_{s}', f'f{fi:05d}.jpg'), os.path.join(dst, f'{s}_关键帧', f'{name}_{t:05.2f}s.jpg'))
    print('ok', s)
