# S04 V2 · LTX 运行记录

## 2026-11-17 第 1 次（失败，没有输出）
- 用户批准预算：预计 $0.25–0.40（A100），最坏约 $1.30；后因 A100 缺货，用户改批 H100 安全云（$4.39/时），看门狗 0.28 小时（约 17 分钟），最坏约 $1.25。
- 之前的阻碍：
  - 00:51–02:00 UTC 起，本容器到 `rest.runpod.io` 一直 502 "upstream request failed"（含不需要密钥的 `/openapi.json`），重存、换新 key 后仍然 502；RunPod 控制台正常，`api.runpod.io`（GraphQL）可用。
  - 新增 `runpod_ltx_gql.py`：建机 / 列表 / 删机改走 GraphQL，其余沿用 `ltx_poc04/runpod_ltx.py`；`api.runpod.io` 的密钥由用户在表单里保存。
  - A100 SXM / PCIe 都是 SUPPLY_CONSTRAINT（没建机，$0）。
- 运行：pod `0vx7szaxxi8z3d`，NVIDIA H100 80GB HBM3，$4.39/时。开机、装环境正常；**下载权重（约 68 GB）到 16.7 分钟还没完成**（第一次 S04 测试只用 54 秒）。到 0.28 小时，pod 内看门狗把自己删除，本机脚本随后删除时报 "pod not found"（说明已删）。之后 `list` 为空。
- 费用：约 16.8 分钟 × $4.39/时 ≈ **$1.23**（估算，以账单为准）。没有生成，没有重试。
- 推测原因：这台机器所在机房从 Hugging Face 下载很慢。具体卡在哪个文件不知道：脚本只在结束时拉 setup.log，pod 被看门狗删了就拿不到。
- 改进（下次）：运行中定时拉 setup.log；考虑用 RunPod 网络存储缓存权重。
