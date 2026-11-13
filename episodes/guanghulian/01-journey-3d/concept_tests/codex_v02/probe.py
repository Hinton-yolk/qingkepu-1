import bpy,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
r=Path(__file__).resolve().parent/'out'
a=json.loads((r/'render_all.json').read_text())[90];cam=bpy.context.scene.camera;cam.location=a['camera_transform'][:3];cam.rotation_euler=a['camera_transform'][3:];bpy.context.view_layer.update()
me=bpy.data.objects['output dynamic field'].data
centers=[sum((me.vertices[j*8+k].co for k in range(8)),Vector())/8 for j in range(len(me.vertices)//8)]
d=[0.]
for p,q in zip(centers,centers[1:]):d.append(d[-1]+(p-q).length)
i=4;p=centers[i];v=world_to_camera_view(bpy.context.scene,cam,p)
res={'native_xy':[v.x*270,(1-v.y)*480],'delay':round(d[i]/d[-1]*90),'world':list(p)}
(r/'probe.json').write_text(json.dumps(res));print(res)
