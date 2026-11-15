#!/bin/bash
# 远景 PoC 05 · V3：首帧换成 GPT 照着灰模首帧画的照片级图（用户 11-14 生成），其余和 V1 相同。输出写到 /w/out。
# 用来回答：首帧不再是我们自己的 Cycles 帧时，LTX 能不能超过 Cycles。
# 灰模：clay_24.mp4（1088×1920，24 fps，145 帧）。隐形标记：--marker-root-path /w/marking（用户 2026-11-14 同意打开）。
cd /w/LTX-2
M=/w/models
PROMPT="Cinematic wide shot inside a data center cold aisle: two long rows of black server racks behind perforated mesh doors with small green and blue status lights and colored patch cables, yellow fiber trays, black cable ladders with bundles of teal cables, pipes and linear LED ceiling lights overhead, a white wall at the end of the aisle, perforated raised floor tiles, light haze, the camera glides down the aisle and turns toward a network switch whose optical modules have lime-green pull tabs, cool blue tones, photoreal."
COMMON=(--transformer-path $M/diffusion_models/ltx-2.5-22b-distilled-transformer-bf16.safetensors
        --text-encoder-path $M/text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors
        --video-vae-path $M/vae/ltx-2.5-video-vae-bf16.safetensors
        --audio-vae-path $M/vae/ltx-2.5-audio-vae-bf16.safetensors
        --spatial-upsampler-path $M/latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors
        --lora $M/lora/ltx-2.5-22b-ic-lora-layout-to-render-1.0.safetensors 1.0
        --stage-2-ic-lora
        --video-conditioning /w/in/clay_24.mp4 1.0
        --height 1920 --width 1088 --num-frames 145 --frame-rate 24 --seed 42
        --quantization fp8-cast
        --marker-root-path /w/marking)

run() {   # $1 名字，其余是额外参数；显存不够时自动加 --offload cpu 重试一次
  name=$1; shift
  t=$(date +%s)
  echo "=== $name 开始 $(date +%H:%M:%S)"
  if ! uv run python -m ltx_pipelines.ic_lora "${COMMON[@]}" --prompt "$PROMPT" "$@" --output-path /w/out/$name.mp4; then
    echo "=== $name 第一遍失败，加 --offload cpu 重试"
    uv run python -m ltx_pipelines.ic_lora "${COMMON[@]}" --prompt "$PROMPT" "$@" --offload cpu --output-path /w/out/$name.mp4 || echo "=== $name 失败"
  fi
  echo "=== $name 用时 $(( $(date +%s) - t )) 秒"
}

nvidia-smi --query-gpu=name,memory.total --format=csv
run v3_gptfirst --image /w/in/kf_first.png 0 1.0

# 检测隐形标记是否嵌入
uv run python - <<'PY'
import glob, torch
from ltx_pipelines.marking import create_markers, detect_audio_mark, detect_video_mark
vm, am = create_markers('/w/marking', torch.device('cuda'))
with open('/w/out/marks.txt', 'w') as f:
    for p in sorted(glob.glob('/w/out/*.mp4')):
        f.write(f'{p}\n  video: {detect_video_mark(vm, p)}\n')
        try:
            f.write(f'  audio: {detect_audio_mark(am, p)}\n')
        except Exception as e:
            f.write(f'  audio: {e!r}\n')
print(open('/w/out/marks.txt').read())
PY
cp /w/run.log /w/out/run_log_snapshot.txt 2>/dev/null
