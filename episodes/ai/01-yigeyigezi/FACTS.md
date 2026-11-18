# FACTS · EP.01 AI 为什么一个字一个字往外蹦？

〔事实〕查得到；〔示意〕〔类比〕〔估算〕片中已加注。

## 1. 大模型一次只生成一个 token，下一个 token 以前面所有 token 为条件〔事实〕
- 片中：「它真的只能一个字一个字地想」「下一个字没定，后面的字根本没法算」。
- 依据：自回归语言模型按 p(x_t | x_<t) 逐个生成；第 t 个 token 采样出来之后，才能作为输入去算第 t+1 个。
- 来源：Vaswani et al., *Attention Is All You Need*, NeurIPS 2017（解码器自回归，§3）；Radford et al., *Language Models are Unsupervised Multitask Learners*（GPT-2 技术报告，2019，§2）。
- 「一个字」严格说是一个 token：中文里一个 token 大致是一个字到一个词，按分词器不同而不同。片中小字已注明。

## 2. 每个 token 都要把整个模型跑一遍〔事实，限定稠密模型〕
- 前向计算每个 token 约 2N 次浮点运算（N = 参数量），也就是每个参数大约用一次。来源：Kaplan et al., *Scaling Laws for Neural Language Models*, arXiv:2001.08361, Table 1。
- 混合专家（MoE）模型每个 token 只用一部分参数，所以小字写「以常见的稠密模型为例」。

## 3. 每个新 token 都要回头看前面所有的 token〔事实〕
- 自注意力：新位置的 query 和前面每个位置的 key 计算相关度。为了不重复计算，前面位置的 key / value 会缓存起来（KV cache），但「看一遍」本身每步都要做，上下文越长，这一步越重。
- 来源：Vaswani et al. 2017（§3.2 注意力）。KV cache 是常见的推理实现，见 Pope et al., *Efficiently Scaling Transformer Inference*, arXiv:2211.05102（§2）。

## 4. 给每个候选字打分，按分数抽签，不总选第一名〔事实，分数为示意〕
- 模型输出词表上的概率分布，常用的解码方式是按概率采样（可用温度、top-p 调整），不一定取最大值。
- 来源：Holtzman et al., *The Curious Case of Neural Text Degeneration*, ICLR 2020（核采样 top-p，以及为什么不总取最大值）。
- 「海 41% · 睡 18% · 爬 12% · 吃 9%」是示意数字，片中已注。

## 5. 一个字内部的乘加是同时算的；同一句话里，字和字之间只能排队〔事实〕
- 单个 token 的前向计算里，矩阵乘法在 GPU 上并行；生成第 t+1 个 token 必须等第 t 个 token 定下来。
- 补充（不进片）：推理服务会把很多用户的请求拼成一批同时算，所以整块显卡不会真的闲着；片中说的是「同一句话」。单条请求逐 token 解码时，速度主要受显存带宽限制，见 Pope et al. 2022。

## 6. 训练时一整段可以同时算〔事实〕
- 训练用现成文本，每个位置的「下一个 token」都已知（teacher forcing）。配合因果掩码，一次前向就能同时得到所有位置的预测和误差，所以训练可以在序列维度上并行，生成却不行。
- 来源：Vaswani et al. 2017（§1 和 §4：Transformer 相对 RNN 可并行训练；解码器用掩码防止看到后面的位置）。

## 7. 投机解码：小模型抢答，大模型一次批改，快 2–3 倍，输出分布不变〔事实〕
- 做法：小的「草稿模型」先连续猜 k 个 token；大模型一次前向同时算这 k 个位置（像训练时一样并行）；从头开始逐个接受，遇到第一个被拒绝的位置，就从修正后的分布里重新采样一个 token，丢掉它后面的草稿。每轮至少前进 1 个 token。
- 质量：这种接受 / 拒绝规则保证输出的概率分布和大模型自己逐个采样完全相同。用贪心解码时，输出的文字也逐字相同。
- 速度：
  - Leviathan, Kalman, Matias, *Fast Inference from Transformers via Speculative Decoding*, ICML 2023（arXiv:2211.17192）：在 T5-XXL 上实测比标准实现快 2–3 倍，输出相同。
  - Chen et al., *Accelerating Large Language Model Decoding with Speculative Sampling*, arXiv:2302.01318（DeepMind，2023）：Chinchilla 70B 上快 2–2.5 倍，样本质量不变。
- 片中「快 2–3 倍」配小字「论文实测，因模型而异」；「质量不打折」配小字「指概率分布相同」。
- 片中「从第一个错处重来」：严格说是在第一个被拒绝的位置换成大模型重新采样的 token。画面上画成「夕」被红笔划掉、换成大模型的「日」，和这个过程一致。
- 不说某个具体产品在用（没有公开依据的不说）。

## 8. 「显卡里上万个核」〔事实〕
- 例：RTX 4090 有 16384 个 CUDA 核心（NVIDIA 规格页）。片中是绿点阵符号，沿用自「AI 为什么非要用显卡？」。

## 9. 「小模型参数少很多，猜得快，但没那么准」〔事实〕
- 投机解码里草稿模型通常比目标模型小一到两个数量级。Leviathan et al. 2023 用 T5-small（7700 万参数）给 T5-XXL（110 亿参数）打草稿；Chen et al. 2023 用 40 亿参数的草稿模型配 700 亿参数的 Chinchilla。
- 「猜得快」：参数少，每个 token 的计算量和要搬的数据都少。「没那么准」：所以要大模型批改。
