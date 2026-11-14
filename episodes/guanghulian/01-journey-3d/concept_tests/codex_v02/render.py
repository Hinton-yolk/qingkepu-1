"""Independent MZI 3D animation. F0..269, no imported T5 executable code or 2D plates."""
import bpy, math, sys, json, time, os
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent;T=json.loads((R/'shot_timeline.json').read_text());O=R/'out';O.mkdir(exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
frames=[int(v) for v in args[0].split(',')] if args and args[0]!='all' else list(range(270))
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.render.engine=os.environ.get('CODEX_RENDER_ENGINE','CYCLES');s.cycles.samples=T['samples'];s.cycles.use_denoising=True;s.cycles.max_bounces=2
s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=540;s.render.resolution_y=960;s.render.resolution_percentage=50;s.render.use_compositing=False;s.render.image_settings.file_format='PNG'
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.render.fps=30
s.world=bpy.data.worlds.new('dark studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.035,.05,.075,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35

def mat(n,c,metal=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Metallic'].default_value=metal;b.inputs['Roughness'].default_value=.42;return m
chip=mat('silicon substrate',(.035,.055,.075),.3);edge=mat('etched ridge',(.09,.14,.18),.2);electrode=mat('inactive electrode metal',(.20,.24,.28),.65);clad=mat('phase shifter body',(.12,.19,.23),.3)
def box(n,loc,scale,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);be=o.modifiers.new('edge bevel','BEVEL');be.width=.06;be.segments=2;return o
box('one shared chip',(0,1,-.28),(12,24,.5),chip)
box('right phase shifter',(2,1.8,.06),(1.0,3.5,.18),clad)
for x in [2.65,3.15]:box('physical traveling-wave electrode',(x,1.0,.17),(.22,5.2,.20),electrode)
box('driver contact',(3.1,-4.5,.10),(1.35,1.3,.25),electrode)
# Sparse etched background detail; never gold/cyan decoration.
for x in [-4.5,-4.1,4.9]:box('etched inactive track',(x,1,.0),(.025,18,.02),edge)

def path(points,steps=12):
 # Catmull-Rom sampled spline through physical control points.
 ps=[Vector(p) for p in points];out=[]
 for k in range(len(ps)-1):
  a,b,c,d=ps[max(0,k-1)],ps[k],ps[k+1],ps[min(len(ps)-1,k+2)]
  for j in range(steps):
   t=j/steps;out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
 out.append(ps[-1]);return out
P={
'input':path([(0,-6,.20),(0,-4.5,.20),(0,-3,.20)]),
'left':path([(0,-3,.20),(-2,-1.5,.20),(-2,3.5,.20),(0,5.5,.20)]),
'right':path([(0,-3,.20),(2,-1.5,.20),(2,3.5,.20),(0,5.5,.20)]),
'output':path([(0,5.5,.20),(.0,7,.20),(1.7,9.5,.20),(3.8,13,.20)]),
'electric':path([(3.1,-4.5,.33),(3.1,-2.5,.33),(2.8,0,.33),(2.7,2.4,.33)])}

def ridge(n,pts,r,m):
 cu=bpy.data.curves.new(n,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for a,p in zip(sp.points,pts):a.co=(*p,1)
 o=bpy.data.objects.new(n,cu);s.collection.objects.link(o);o.data.materials.append(m)
for n,pts in P.items():ridge(n+' physical guide',pts,.16 if n!='electric' else .21,edge if n!='electric' else electrode)

def glow_material(n,color):
 m=bpy.data.materials.new(n);m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(*color,1);a=nt.nodes.new('ShaderNodeAttribute');a.attribute_name='power';nt.links.new(a.outputs['Fac'],em.inputs['Strength']);nt.links.new(em.outputs[0],out.inputs[0]);return m
cyan=glow_material('guided IR visualization',(.02,.65,.82));gold=glow_material('electrical level visualization',(1,.42,.035))
fields={}
for name,pts in P.items():
 verts=[];faces=[]
 for i,p in enumerate(pts):
  tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();u=tangent.cross(Vector((0,0,1))).normalized();v=tangent.cross(u).normalized()
  for k in range(8):verts.append(p+Vector((0,0,.20))+.085*(u*math.cos(k*math.tau/8)+v*math.sin(k*math.tau/8)))
 for i in range(len(pts)-1):
  for k in range(8):faces.append((i*8+k,i*8+(k+1)%8,(i+1)*8+(k+1)%8,(i+1)*8+k))
 me=bpy.data.meshes.new(name+' dynamic field');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name+' dynamic field',me);s.collection.objects.link(o);o.data.materials.append(gold if name=='electric' else cyan)
 a=me.attributes.new('power','FLOAT','POINT');dist=[0.0]
 for p,q in zip(pts,pts[1:]):dist.append(dist[-1]+(q-p).length)
 fields[name]=(me,a,dist)
# Slight relief and electrode connection to one arm, no fake photons in free space.
box('phase bridge',(2.43,2.35,.24),(.82,.4,.15),electrode)
# Perspective camera 32deg above chip, rather than top-down orthographic board.
cd=bpy.data.cameras.new('director camera');cam=bpy.data.objects.new('director camera',cd);s.collection.objects.link(cam);s.camera=cam;cd.lens=47;cd.sensor_fit='VERTICAL';cd.sensor_height=24
for loc,en,size in [((-6,-5,12),1700,10),((5,7,10),2200,8)]:
 l=bpy.data.lights.new('softbox','AREA');l.energy=en;l.size=size;o=bpy.data.objects.new('softbox',l);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(-Vector(loc)).to_track_quat('-Z','Y').to_euler()
# Image-space glow kept restrained: geometry remains legible.
try:
 ng=bpy.data.node_groups.new('restrained optical bloom','CompositorNodeTree');s.compositing_node_group=ng;ng.interface.new_socket('Image',in_out='OUTPUT',socket_type='NodeSocketColor');rl=ng.nodes.new('CompositorNodeRLayers');rl.scene=s;gl=ng.nodes.new('CompositorNodeGlare');gl.inputs['Type'].default_value='Fog Glow';gl.inputs['Threshold'].default_value=1.3;gl.inputs['Strength'].default_value=.12;go=ng.nodes.new('NodeGroupOutput');ng.links.new(rl.outputs['Image'],gl.inputs['Image']);ng.links.new(gl.outputs['Image'],go.inputs[0])
except Exception as e:print('COMPOSITOR_ERROR',e);raise

def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def bit_at(f,starts):
 if f<starts[0]:return None
 return T['pattern'][min(7,max(0,int((f-starts[0])//12)))]
def camera(f):
 # Four blocks share the same projection at each cut. Motion settles before S3.
 if f<=44:
  u=smooth(f/44);target=Vector((0,1.2+.25*u,0));dist=30.0-1.5*u
 elif f<=89:
  u=smooth((f-45)/44);target=Vector((.35*u,1.45,0));dist=28.5
 elif f<=194:target=Vector((.35,1.45,0));dist=28.5
 else:
  u=smooth((f-195)/74);target=Vector((.35+.45*u,1.45+1.2*u,0));dist=28.5
 cam.location=target+Vector((0,-dist*math.cos(math.radians(32)),dist*math.sin(math.radians(32))));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 return list(cam.location)+list(cam.rotation_euler)

def update(f):
 transform=camera(f)
 elec=bit_at(f,T['electric_starts']);phase=0 if elec==1 else 1.98
 for name,(me,attr,dist) in fields.items():
  vals=[];L=dist[-1]
  for i,d in enumerate(dist):
   if name=='input':power=2.0 # constant at every frame; never carries bits
   elif name in ['left','right']:
    # Small phase texture on the two arms, not an amplitude gate.
    shift=phase if name=='right' and P[name][i].y>.0 else 0
    power=1.3*(.55+.45*math.cos(d*5-f*.18+shift))
   elif name=='electric':
    # First bit enters at F055 and reaches the electrode endpoint at F096.
    # The same eight-bit train advects continuously; zero is a lower level.
    source=f+round((1-d/L)*41)
    v=bit_at(source,T['electric_starts'])
    power=((2.8 if v==1 else .32) if v is not None else .005) if f<195 else .03
   else:
    source=f-round(d/L*90)
    v=bit_at(source,T['optical_starts'])
    optical_phase=0.0 if v==1 else 1.98
    normalized_intensity=(1+math.cos(optical_phase))/2
    power=2.2*normalized_intensity**2.3 # illustrative display contrast; not an extinction-ratio claim
   vals.extend([power]*8)
  attr.data.foreach_set('value',vals);me.update()
 # Phase slab remains a physical part: local refraction-state indication via material only.
 b=clad.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=((.10,.25,.29,1) if elec==1 else (.075,.12,.15,1))
 return transform

def screen(p):
 bpy.context.view_layer.update();v=world_to_camera_view(s,cam,Vector(p));return [v.x*540,(1-v.y)*960,v.z]
records=[]
for f in frames:
 ts=time.time();tr=update(f);s.frame_set(f+1);s.render.filepath=str(O/f'f{f:03d}.png')
 if not (len(frames)==270 and Path(s.render.filepath).exists()):bpy.ops.render.render(write_still=True)
 records.append({'frame':f,'camera_transform':tr,'seconds':time.time()-ts,'anchors':{k:screen(p) for k,p in {'input':(0,-6,.2),'split':(0,-3,.2),'action':(3,2.4,.33),'combine':(0,5.5,.2),'output':(1,8.5,.2)}.items()},'electric':bit_at(f,T['electric_starts']),'optical_source':bit_at(f,T['optical_starts'])})
 print('FRAME',f,round(time.time()-ts,3),flush=True)
(O/('render_all.json' if len(frames)==270 else 'render_test.json')).write_text(json.dumps(records,indent=2))
if len(frames)==270:bpy.ops.wm.save_as_mainfile(filepath=str(O/'director_v02.blend'))
