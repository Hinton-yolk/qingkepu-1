from pathlib import Path
import json,subprocess,hashlib
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;O=R/'out';T=json.loads((R/'shot_timeline.json').read_text())
assert all((O/f'f{f:03d}.png').exists() for f in range(270)), 'Missing frames: stop, never nearest-frame fill'
for f in range(270):assert Image.open(O/f'f{f:03d}.png').size==(270,480)
v=O/'Director_Locked_V02_9s_silent.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-framerate','30','-start_number','0','-i',str(O/'f%03d.png'),'-frames:v','270','-vf','scale=540:960:flags=lanczos','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(v)],check=True)
font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',17)
def sheet(fs,name,cols=5):
 im=Image.new('RGB',(270*cols,506*((len(fs)+cols-1)//cols)),(8,14,22));d=ImageDraw.Draw(im)
 for i,f in enumerate(fs):
  x=i%cols*270;y=i//cols*506;im.paste(Image.open(O/f'f{f:03d}.png'),(x,y));d.text((x+8,y+482),f'F{f:03d}  {f/30:.3f}s',font=font,fill='white')
 im.save(O/name,quality=90)
sheet([0,22,44,45,67,89,90,95,96,100,108,112,120,136,160,184,194,195,232,269],'keyframes_20.jpg')
sheet([x for e,o in zip(T['electric_starts'],T['optical_starts']) for x in [e-1,o]],'S3_bit_edges.jpg',4)
sheet([f for c in [45,90,195] for f in range(c-3,c+3)],'cut_neighborhoods.jpg',6)
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(v)]));(O/'ffprobe.json').write_text(json.dumps(meta,indent=2))
s=meta['streams'];assert len(s)==1 and s[0]['codec_name']=='h264';assert (s[0]['width'],s[0]['height'],s[0]['r_frame_rate'],int(s[0]['nb_read_frames']))==(540,960,'30/1',270);assert abs(float(meta['format']['duration'])-9)<1e-6
records=json.loads((O/'render_all.json').read_text());assert [r['frame'] for r in records]==list(range(270))
assert len({tuple(r['camera_transform']) for r in records[90:195]})==1
cuts={str(c):max(abs(a-b) for a,b in zip(records[c-1]['camera_transform'],records[c]['camera_transform'])) for c in [45,90,195]}
assert all(x<1e-6 for x in cuts.values())
# Encoded-video pixel probes: actual delivery, not only timeline constants.
import numpy as np
raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(v),'-vf','scale=270:480','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);a=np.frombuffer(raw,np.uint8).reshape(270,480,270,3)
# A fixed S3 input point and a point just above the combiner on the output guide.
def roi(f,name,offset=(0,0),rad=1):
 x,y,_=records[f]['anchors'][name];x=round((x+offset[0])/2);y=round((y+offset[1])/2);return a[f,y-rad:y+rad+1,x-rad:x+rad+1,:].mean()
input_values=[roi(f,'input',(0,-7)) for f in range(90,195)]
# 10px above combiner includes only output, not the split arms.
probe=json.loads((O/'probe.json').read_text());x,y=map(round,probe['native_xy'])
values=[float(a[o+probe['delay']+4,y-1:y+2,x-1:x+2].mean()) for o in T['optical_starts']]
bright=[v for v,b in zip(values,T['pattern']) if b];dark=[v for v,b in zip(values,T['pattern']) if not b];ratio=float(np.mean(bright)/max(1,np.mean(dark)))
result={'specification':'PASS','all_270_native_frames':True,'source_frame_size':[270,480],'delivery_size':[540,960],'S3_camera_locked':True,'cut_transform_deltas':cuts,'input_pixel_minmax_S3':[min(input_values),max(input_values)],'output_bit_probe_values':values,'output_bright_dark_ratio':ratio,'contrast_target_2_5':ratio>=2.5,'total_render_seconds_recorded':sum(r['seconds'] for r in records),'sha256':hashlib.file_digest(v.open('rb'),'sha256').hexdigest(),'first_look_humans':'NOT VERIFIED','director_approval':'NOT ASSESSED'}
(O/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
