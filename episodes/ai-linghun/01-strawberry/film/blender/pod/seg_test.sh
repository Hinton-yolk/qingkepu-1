# test-render a few frames of each hybrid segment: /w/in/seg_<f0>_<f1>.tgz (scene.glb, anim.json, screen/) + /w/in/build.py; frames in /w/in/test_frames.txt ("<seg> <frame>" per line)
set -x
export KEPU_GPU=OPTIX
mkdir -p /w/bld /w/out/segtest && cp /w/in/build.py /w/bld/build.py
for t in /w/in/seg_*.tgz; do n=$(basename $t .tgz); n=${n#seg_}; [ -d /w/bld/$n ] || { mkdir -p /w/bld/$n && tar xzf $t -C /w/bld/$n; }; done
while read seg f; do
  /w/bl/blender -b --python-exit-code 1 --python /w/bld/build.py -- /w/out/segtest $f $f ${SAMPLES:-128} cycles gpu 1.0 /w/bld/$seg 2>&1 | grep -E "segment:|screen sequence|missing|Error|rendered|Traceback" | tail -5
done < /w/in/test_frames.txt
ls -la /w/out/segtest
