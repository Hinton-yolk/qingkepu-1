# EP.06 手表绿光 · FACTS（白话版阶段，2026-11-14）

来源等级：〔官〕厂商官方文档；〔综〕综述 / 论文；〔厂〕厂商宣传，未经独立验证；〔待〕还没找到可靠来源，进脚本前要补。
脚本定稿时由审核用最强模型做事实核查。

| # | 片中说法 | 事实 | 来源 |
|---|---|---|---|
| 1 | 背面的绿灯 + 「光眼睛」 | Apple Watch 用绿色 LED 配光电二极管，探测手腕里的血流量 | 〔官〕Apple 支持「Monitor your heart rate with Apple Watch」https://support.apple.com/en-us/120277 |
| 2 | 血是红的，因为它吃掉绿光 | Apple 原文：「Blood is red because it reflects red light and absorbs green light」。严格说：血红蛋白在绿光（约 500–600 nm）吸收强、在红光吸收弱 | 〔官〕同上；〔综〕多波长 PPG 综述（IEEE, https://ieeexplore.ieee.org/abstract/document/9582790） |
| 3 | 心跳一下血多一点，吃掉的绿光多一点 | 心跳时手腕血流增多，绿光吸收增多；两次心跳之间减少 | 〔官〕同 1 |
| 4 | 一秒闪几百次 | 原文「flashing its LED lights hundreds of times per second」 | 〔官〕同 1 |
| 5 | 为什么用绿光（如需要） | 绿光被血红蛋白吸收强、脉动信号大；穿透较浅，对运动干扰较不敏感，所以腕上设备常用 | 〔综〕JMIR mHealth 2024 https://mhealth.jmir.org/2024/1/e57158 ；PMC7612541 |
| 6 | 手一甩，光也跟着变；加速度计把甩的那份减掉 | 运动伪影是腕式 PPG 的主要误差来源；常用做法是用同一设备的加速度计信号做谱减法 / 自适应滤波，把运动成分从 PPG 里去掉 | 〔综〕Mashhadi 等 arXiv:1504.04785；PARHELIA（IEEE TBME 2017）；PMC6450646 |
| 7 | 戒指用的是同一招 | Oura：PPG，LED 打光、光电二极管读反射光；每秒采样 250 次；LED 放在手指两侧 | 〔厂〕https://ouraring.com/blog/ring-technology/ |
| 8 | （不进片，备查）戒指 / 夜里用红外 | Oura 称用红外光，比绿光穿得深；Apple 支持页称新款手表在睡眠时段改用红外 LED | 〔厂〕同 7；〔官〕同 1 |
| 9 | （不进片，备查）手指信号更好 | Oura 博客引 2019 年六部位对比研究：手指可分析波形比例最高 | 〔厂〕https://ouraring.com/blog/accuracy-of-finger-worn-wearables/ ；〔待〕找原文 |
| 10 | 医院夹手指的血氧仪，也是用光看血 | 指夹式血氧仪用红光（约 660 nm）和红外光穿过手指，比较两者吸收算血氧；脉率来自随心跳变化的那部分吸收 | 〔官〕FDA 510(k) 摘要 https://510k.innolitics.com/device/K212300 ；MedlinePlus https://magazine.medlineplus.gov/article/getting-an-accurate-read-on-pulse-oximeters |
| 11 | 表带戴紧、戴在腕骨上面、别晃 | Garmin 手册：戴在腕骨上方，贴合但舒适，跑步时不要移动；Apple：「snug but comfortable」 | 〔官〕Garmin 手册 https://www8.garmin.com/manuals/webhelp/venu/EN-US/GUID-F2E7E0A9-FB44-4297-BF4D-D0C31C400C45.html ；〔待〕Apple 现行原文 |
| 12 | 深色纹身可能测不准 | Apple 2015 年支持页：部分纹身的墨水、图案、饱和度会挡住传感器的光；实测深色实心墨水影响最大 | 〔官〕转引自 Engadget https://www.engadget.com/2015-05-01-apple-watch-tattoo-confirmation.html ；〔待〕Apple 现行页面原文 |

## 注意
- 「一亮一暗」是简化：真实信号是在一个很大的不变底上叠一点点随心跳的起伏，画面上要放大起伏，并加注「起伏放大示意」。
- 不写具体型号（Series 几、Ultra 几），也不点评哪个牌子准。
- 心率 72 是示意数字。
