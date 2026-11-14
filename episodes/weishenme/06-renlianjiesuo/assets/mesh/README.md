# 人脸网格的来源

- `canonical_face_model.obj`：Google MediaPipe 的标准人脸网格（canonical face model），Apache License 2.0。
  来源：github.com/google-ai-edge/mediapipe，`mediapipe/modules/face_geometry/data/canonical_face_model.obj`（2026-11-11 下载）。
- `face.js`：由 `tools/mesh.py` 生成（Loop 细分两次，加上口红、腮红、眼影、修容、眼周、口罩各区域的权重）。
- 片中只用它画「手机量到的数据」（光点、等高线）；人物是手绘插画（`portrait.js`）。
- 发布文案里署名：「人脸网格：Google MediaPipe（Apache-2.0）」。
