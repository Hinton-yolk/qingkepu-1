#!/bin/bash
# PROJECT LIGHTPATH · S04 三关键帧 LTX 测试（在 RunPod 上执行，输出写到 /w/out）。
# 灰模：clay_24.mp4 = V1.1 S04 的相机和硬件，Workbench 统一灰，无信号指示；1088×1920，24 fps，121 帧（5.04 s），
#       LTX 第 k 帧 = S04 局部帧 1 + k×149/120（第 0 / 72 / 120 帧 = F001 / F090.4 / F150）。
# 关键帧：用户用 GPT Image 照灰模 F001 / F090 / F150 画的三张照片（941×1672 → 高 1920、两侧各补 3–4 像素到 1088 宽）。
# 设置照抄 PoC 04 / 远景 PoC 05 跑通的那套（LTX-2.5 22B distilled + Layout-To-Render IC-LoRA，fp8-cast，seed 42）。
# 隐形标记打开（--marker-root-path），用户 2026-11-14 同意。
cd /w/LTX-2
M=/w/models
PROMPT="Photorealistic cinematic shot inside an AI data center. The camera starts close on a silver OSFP optical transceiver plugged into the I/O panel of a server, with an aqua MPO fiber connector, a black strain-relief boot and an aqua fiber-optic cable curving away and down. The camera smoothly pulls back and rises to reveal two adjacent black server racks with open-top GPU servers, green circuit boards and aluminium heatsinks; the same single aqua fiber cable drops into a perforated steel horizontal cable tray below the top servers and runs across to the neighboring rack. The camera then glides toward the receiving server and settles on its OSFP transceiver and aqua MPO connector, with the cable arriving from below. Brushed aluminium, dark powder-coated steel, small green status LEDs, neutral studio lighting, shallow depth of field, steady physical camera, no visual effects, no glow, no particles."
COMMON=(--transformer-path $M/diffusion_models/ltx-2.5-22b-distilled-transformer-bf16.safetensors
        --text-encoder-path $M/text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors
        --video-vae-path $M/vae/ltx-2.5-video-vae-bf16.safetensors
        --audio-vae-path $M/vae/ltx-2.5-audio-vae-bf16.safetensors
        --spatial-upsampler-path $M/latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors
        --lora $M/lora/ltx-2.5-22b-ic-lora-layout-to-render-1.0.safetensors 1.0
        --stage-2-ic-lora
        --video-conditioning /w/in/clay_24.mp4 1.0
        --height 1920 --width 1088 --num-frames 121 --frame-rate 24 --seed 42
        --quantization fp8-cast
        --marker-root-path /w/marking)

run() {   # $1 名字，其余是额外参数；显存不够时自动加 --offload cpu 重试一次（同一台机器内，不另开机）
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
run s04_ltx_3keys --image /w/in/kf_first.png 0 1.0 --image /w/in/kf_mid.png 72 1.0 --image /w/in/kf_last.png 120 1.0

uv run python - <<'PY'
import glob, torch
from ltx_pipelines.marking import create_markers, detect_video_mark
vm, am = create_markers('/w/marking', torch.device('cuda'))
with open('/w/out/marks.txt', 'w') as f:
    for p in sorted(glob.glob('/w/out/*.mp4')):
        f.write(f'{p}\n  video: {detect_video_mark(vm, p)}\n')
print(open('/w/out/marks.txt').read())
PY
cp /w/run.log /w/out/run_log_snapshot.txt 2>/dev/null
