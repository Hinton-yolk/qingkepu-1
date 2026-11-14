# EP.06 手表绿光 · FACTS（白话版阶段，2026-11-14）

来源等级：〔官〕厂商官方文档；〔综〕综述 / 论文；〔厂〕厂商宣传，未经独立验证；〔待〕还没找到可靠来源，进脚本前要补。
脚本定稿时由审核用最强模型做事实核查。

| # | 片中说法 | 事实 | 来源 |
|---|---|---|---|
| 1 | 背面的绿灯 + 「光眼睛」 | Apple Watch 用绿色 LED 配光电二极管，探测手腕里的血流量 | 〔官〕Apple 支持「Monitor your heart rate with Apple Watch」https://support.apple.com/en-us/120277 |
| 2 | 血是红的，因为它吃掉绿光 | Apple 原文：「Blood is red because it reflects red light and absorbs green light」。严格说：血红蛋白在绿光（约 500–600 nm）吸收强、在红光吸收弱 | 〔官〕同上；〔综〕Prahl / OMLC 血红蛋白摩尔消光系数 https://omlc.org/spectra/hemoglobin/summary.html ：HbO2 约 414 nm 524 280、530 nm 39 957、660 nm 320 cm⁻¹/M —— 绿光约为红光的 125 倍，蓝紫光又约为绿光的 13 倍。**所以不能说「只有绿光被吃」**，只能说「绿光被吃得多，红光被弹回来」 |
| 3 | 心跳一下血多一点，吃掉的绿光多一点 | 心跳时手腕血流增多，绿光吸收增多；两次心跳之间减少 | 〔官〕同 1 |
| 4 | 一秒闪几百次 | 原文「flashing its LED lights hundreds of times per second」 | 〔官〕同 1 |
| 5 | 为什么用绿光（如需要） | 绿光被血红蛋白吸收强、脉动信号大；穿透较浅，对运动干扰较不敏感，所以腕上设备常用 | 〔综〕JMIR mHealth 2024（PMC11470225）https://mhealth.jmir.org/2024/1/e57158 ：「Green light is typically used because it offers shallower penetration and greater robustness against motion artifacts」；Charlton 等 2022（PMC7612541）：绿光比红光、红外进得浅；不用蓝光：进得太浅、黑色素吸收强（TI https://ti.com/lit/pdf/sszt538 ） |
| 6 | 手一甩，光也跟着变；加速度计把甩的那份减掉 | 运动伪影是腕式 PPG 的主要误差来源；常用做法是用同一设备的加速度计信号做谱减法 / 自适应滤波，把运动成分从 PPG 里去掉 | 〔综〕Chung 2019 PLoS One（PMC6450646，用加速度计功率谱做谱减法；也指出传感器和手腕之间的压力变化是运动干扰来源）；Charlton 2022（PMC7612541，运动参考信号：加速度计、陀螺仪、另一波长 PPG）；〔厂〕Polar 白皮书 https://www.polar.com/en/guide/optical-heart-rate-monitoring-polar-precision-prime 。Apple / Garmin 未公开算法，「减掉」是简化说法；节律性运动（跑步、骑车）比网球、拳击准（Apple https://support.apple.com/zh-cn/105002 ） |
| 7 | 戒指用的是同一招 | Oura：PPG，LED 打光、光电二极管读反射光；每秒采样 250 次；LED 放在手指两侧 | 〔厂〕https://ouraring.com/blog/ring-technology/ |
| 8 | （不进片，备查）戒指 / 夜里用红外 | Oura 称用红外光，比绿光穿得深；Apple 支持页称新款手表在睡眠时段改用红外 LED | 〔厂〕同 7；〔官〕同 1 |
| 9 | （不进片，备查）手指信号更好 | Oura 博客引 2019 年六部位对比研究：手指可分析波形比例最高 | 〔厂〕https://ouraring.com/blog/accuracy-of-finger-worn-wearables/ ；〔待〕找原文 |
| 10 | 医院夹手指的血氧仪，也是用光看血 | 指夹式血氧仪用红光（约 660 nm）和红外光穿过手指，比较两者吸收算血氧；脉率来自随心跳变化的那部分吸收 | 〔官〕FDA 510(k) 摘要 https://510k.innolitics.com/device/K212300 ；MedlinePlus https://magazine.medlineplus.gov/article/getting-an-accurate-read-on-pulse-oximeters |
| 11 | 表带戴紧、戴在腕骨上面、别晃 | Garmin 手册：戴在腕骨上方，贴合但舒适，跑步时不要移动；Apple：「snug but comfortable」 | 〔官〕Garmin 手册（「above your wrist bone」「snug but comfortable」）https://www8.garmin.com/manuals/webhelp/venu/EN-US/GUID-F2E7E0A9-FB44-4297-BF4D-D0C31C400C45.html ；Apple https://support.apple.com/zh-cn/118234 ：「舒适贴合」「戴在腕骨以上（靠近肘部，而不是手部）」「锻炼时可以收紧，结束后放松」。**注意：「戴在腕骨上面」会被读成压在腕骨上，正是官方要纠正的戴法** |
| 12 | 深色纹身可能测不准 | Apple 2015 年支持页：部分纹身的墨水、图案、饱和度会挡住传感器的光；实测深色实心墨水影响最大 | 〔官〕Apple 现行 https://support.apple.com/zh-cn/105002 ：「一些纹身所使用的色料、图案和饱和度可能会阻碍传感器检测到相应的光线」。官方没说「大面积深色」——「深色实心影响最大」出自 2015 年媒体实测（Engadget 转引 https://www.engadget.com/2015-05-01-apple-watch-tattoo-confirmation.html ）；片中小字用官方口径「有些纹身会挡光」 |
| 13 | 戒指内圈两侧的小灯亮绿光（画面） | Oura 官方：Ring 4「Green and infrared LEDs … alternate to measure heart rate and HRV 24/7」，红光 + 红外测睡眠血氧；LED 在手指两侧 → 画面画内圈两侧的绿光有依据。各品牌不同，不点名 | 〔厂〕https://ouraring.com/blog/smart-sensing/ ；同 7（ring-technology 页只提红外，是旧说法） |
| 14 | 读数 72 / 128（v2 建议改 80 / 120，示意） | 示意数字，不代表任何人的标准值 | — |

| 15 | 「这叫光电容积描记」（小字） | 方法名：光电容积描记（法）/ 光电容积脉搏波描记法，PPG；「脉搏波」是信号名。Apple 中文用「光体积描记法」 | 〔官〕https://support.apple.com/zh-cn/120277 ；〔综〕《医用生物力学》2024 https://search.napstic.cn/literature/periodical/010yyswlx202402025 |
| 16 | 光在组织里的路径（画面） | 漫散射、弯曲路径，不是镜面反弹；绿光只到真皮浅层的小动脉和毛细血管网；也有研究认为绿光 PPG 主要来自动脉搏动对毛细血管床的挤压 | 〔综〕Kamshilin 2015 https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4440202/ |
| — | 「光眼睛」 | **类比**：指光电二极管，小字给出真名 | — |

## 注意
- 「一亮一暗」是简化：真实信号是在一个很大的不变底上叠一点点随心跳的起伏，画面上要放大起伏，并加注「起伏放大示意」。
- 不写具体型号（Series 几、Ultra 几），也不点评哪个牌子准。
- 心率 72 是示意数字。
