# render the test stills uploaded as /w/in/st<frame>_scene.glb + st<frame>_anim.json with /w/in/build.py
set -x
export KEPU_GPU=OPTIX
SAMPLES=${SAMPLES:-128}
mkdir -p /w/bld && cp /w/in/build.py /w/bld/build.py
for g in /w/in/st*_scene.glb; do
  f=$(basename $g _scene.glb); f=${f#st}; d=/w/bld/st$f; mkdir -p $d
  cp $g $d/scene.glb; cp /w/in/st${f}_anim.json $d/anim.json
  /w/bl/blender -b --python-exit-code 1 --python /w/bld/build.py -- /w/out/stills $((10#$f)) $((10#$f)) $SAMPLES cycles gpu 1.0 $d 2>&1 | grep -E "missing|Error|error|rendered|Time:" | tail -6
done
ls -la /w/out/stills
