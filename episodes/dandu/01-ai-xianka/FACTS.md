# FACTS · AI 为什么非要用显卡？

每条：片中怎么说 → 依据 → 来源。〔事实〕查得到的数据；〔估算〕写明假设；〔示意〕〔类比〕片中已加注。

## 1. 说一个字约 70 亿次乘加〔估算〕
- 片中：「说一个字，要做约 70 亿次」；小字「估算：70 亿参数的模型，每说一个字（token）约 70 亿次乘加」。
- 依据：Transformer 前向计算每个 token 约 2N 次浮点运算（N = 参数量），一次乘加 = 2 次运算，所以约 N 次乘加。70 亿参数 → 约 70 亿次乘加。
- 假设：不计注意力部分随上下文长度增长的那一项（2·n_layer·n_ctx·d_attn），上下文短时它比 2N 小得多；「一个字」严格说是一个 token，中文里一个 token 大致是一到两个字。
- 来源：Kaplan et al., *Scaling Laws for Neural Language Models*, arXiv:2001.08361 (2020)，Table 1：C_forward ≈ 2N + 2·n_layer·n_ctx·d_attn。

## 2. 「每个字会变成几千个数」「要一层接一层算几十层」〔事实，片中画面为示意〕
- 例：LLaMA-7B 的隐藏维度 4096，32 层。
- 来源：Touvron et al., *LLaMA: Open and Efficient Foundation Language Models*, arXiv:2302.13971 (2023)，Table 2。
- 片中只画 8 个数、一层 5×8 的数字表，并加注「示意」。

## 3. 候选字概率「光 62%、亮 18%、财 9%、呆 3%」〔示意〕
- 虚构的示意数字，只为说明「算出每个候选字的可能性，取最可能的」。

## 4. CPU「几位数学教授」、GPU「一万多个小学生」〔类比〕
- 片中字幕旁有「类比」标签。
- CPU 画了 8 个核〔示意〕。家用 CPU 常见 8–24 核，例如 Intel Core i9-14900K 24 核（8 性能核 + 16 能效核）、AMD Ryzen 9 9950X 16 核（两家官网规格页）。
- 「示意：真实 CPU 的每个核，一次也能算好几道」：CPU 核有 SIMD 向量单元（如 AVX2 / AVX-512），一条指令同时算多个数。

## 5. RTX 4090 有 16384 个 CUDA 核心〔事实〕
- 来源：NVIDIA GeForce RTX 4090 规格页（NVIDIA CUDA Cores: 16384）；NVIDIA Ada Lovelace 架构白皮书：RTX 4090 启用 128 个 SM，每个 SM 128 个 CUDA 核心。
- 片中画法：128 个 SM（8 列 × 16 行），每个 SM 16 × 8 = 128 个小格，共 16384 个，「一个不少全画了」。SM 布局、L2 带的位置是示意，不是真实版图。
- 小字「GPU 的“核”比 CPU 的核简单得多，不能一个顶一个比」：CUDA 核心是 SM 里的一条浮点 / 整数运算通道，没有自己的取指、分支预测、乱序执行，和 CPU 核不是一回事。

## 6. 「CPU 芯片多半用来“想”和“记”，GPU 更多用来“算”」〔事实，面积比例为示意〕
- 依据：CPU 把大量晶体管花在缓存和流程控制（分支预测、乱序执行）上，以缩短单个任务的延迟；GPU 把更多晶体管花在数据运算单元上，以提高总吞吐。
- 来源：NVIDIA, *CUDA C++ Programming Guide*, 1.1 “The Benefits of Using GPUs”，图 “The GPU Devotes More Transistors to Data Processing”。
- 片中「想」= 调度 / 控制，「记」= 缓存，「算」= 运算单元。面积比例不精确，已加注。

## 7. 同一步里的乘法「谁也不用等谁」；一层等一层〔事实〕
- 矩阵乘法里每个输出元素是一行和一列的点积，彼此独立，可以同时算；神经网络第 k+1 层要用第 k 层的结果，层与层之间是先后关系。
- 这是数学性质，无需外部来源。

## 8. 4K 屏 3840×2160 ≈ 829 万像素，每秒要画几十到上百遍〔事实〕
- 3840 × 2160 = 8,294,400。消费级 4K UHD 分辨率（ITU-R BT.2020 定义的 UHDTV1 为 3840×2160）。
- 游戏帧率常见 30–144 帧 / 秒，按游戏和硬件不同。
- 「各算各的颜色」：渲染管线里像素着色器（fragment shader）对每个像素（片元）各执行一遍，彼此独立，所以 GPU 能并行。

## 9. 2012 年两块游戏显卡训练出 AlexNet，ImageNet 一战成名〔事实〕
- 两块 NVIDIA GTX 580（3 GB），训练 5–6 天；ILSVRC-2012 前 5 错误率 15.3%，第二名 26.2%。
- 来源：Krizhevsky, Sutskever, Hinton, *ImageNet Classification with Deep Convolutional Neural Networks*, NIPS 2012（摘要和第 7 节）。
- 片中画「猫 ✓」是示意：ImageNet 有 1000 类，其中包括几种猫。

## 没放进片子、置顶评论可以补的
- AI 用 GPU 除了核多，还因为显存带宽大（HBM），能把海量参数及时喂给运算单元；现在的 AI 专用 GPU 还有专门算矩阵的 Tensor Core。
