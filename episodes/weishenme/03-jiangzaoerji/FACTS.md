# FACTS — EP.02 降噪耳机（主动降噪）

| 屏上说法 | 依据 |
|---|---|
| 降噪不是"堵得更严"，而是往耳朵里加一个反向的声音 | 主动降噪（ANC）用麦克风拾取噪声，由芯片生成反相信号经扬声器播放，与噪声叠加相消；耳塞的物理隔绝（被动降噪）主要对高频起作用，从约 500 Hz 起逐渐生效。见 [Electronic Design](https://www.electronicdesign.com/technologies/analog/article/21789816/challenges-await-in-noise-cancelling-headset-design) |
| 外侧麦克风 + 内侧麦克风（"只听外面够吗？"） | 前馈（feedforward）麦克风在外侧先听到噪声；反馈（feedback）麦克风在耳道一侧，测量残余噪声并修正；两者结合即混合降噪（hybrid ANC）。见 [ICSV25, Rivera/Papantoni/Zölzer](https://www.hsu-hh.de/ant/wp-content/uploads/sites/699/2018/08/ICSV25_full_paper_Rivera_Papantoni_Zoelzer.pdf)、[USPTO 11978429](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11978429) |
| 低沉的轰隆声最好消（地铁、飞机） | 前馈 ANC 主要对 1 kHz 以下的稳态低频噪声有效；延迟主要限制 1–2 kHz 以上的效果。同上 |
| 反得慢一点就抵消不掉；芯片要在几十微秒里算完 | 麦克风到扬声器典型间距约 0.7 cm，声音走过只需约 20 µs，处理延迟必须在这个量级内；延迟越大，可抵消的频率越低。见 [Electronic Design](https://www.electronicdesign.com/technologies/analog/article/21789816/challenges-await-in-noise-cancelling-headset-design)、[USPTO 11626097](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11626097) |
| 外壳小孔后面的麦克风（v3 起不再标尺寸、不再比芝麻） | TWS 耳机常用 MEMS 麦克风封装 3.5 × 2.65 × 1.0 mm（Infineon IM70A135 面向 TWS 耳机；TDK T5828 同尺寸）。见 [Infineon IM70A135](https://infineon.com/cms/en/product/sensor/mems-microphones/mems-microphones-for-consumer/im70a135)、[TDK T5808](https://invensense.tdk.com/products/digital/t5808) |
| 耳道约 2.5 cm 长、约 7 mm 粗；鼓膜约 1 cm | 外耳道约 2.5 cm，最窄处约 0.7 cm；鼓膜直径约 9–10 mm。见 [Thieme CT 研究](https://thieme-connect.de/products/ejournals/html/10.1055/s-0042-1758213)、[Hearing Health Matters](https://hearinghealthmatters.org/waynesworld/2014/human-ear-canal-iii/) |
| 低沉的噪音每秒振动上百次 | 地铁、飞机舱内噪声能量集中在几十到几百赫兹（1 Hz = 每秒振动一次）。屏上波形为慢放示意 |
| 耳塞没戴紧，噪音会从缝里漏进来；耳朵这头的第二个麦克风听到"还剩多少"，芯片再补 | 反馈（feedback）麦克风测量抵消后的残余（误差信号），自适应滤波器据此不断修正反向信号；佩戴密封直接影响降噪效果。见 [USPTO 11626097](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11626097)、[X-Press：降噪如何工作](https://xpressmag.com.au/noise-cancelling-in-earbuds-how-it-works-and-why-it-matters/) |
| 自适应：周围变吵就多抵消、变安静就少抵消，耳机自己跟着调 | 自适应模式按环境噪声增强或减弱降噪；苹果"自适应音频"会在降噪与通透之间平滑地自动调整。见 [Anker](https://www.anker.com/uk/blogs/earbuds/anc-earbuds-meaning)、[IT之家](https://www.ithome.com/0/721/721.htm)、[Engadget](https://www.engadget.com/airpods-pro-adaptive-audio-preview-automatically-adjusting-to-your-day-130051605.html) |
| 戴久了耳朵胀：其实气压没变，是大脑的误会 | 开关降噪时测不到真实的气压差；低频被大量抵消、降噪突然开启时最容易出现"被吸住"的感觉；多数人会慢慢适应，切到通透可缓解。见 [SoundStage](https://soundstagesolo.com/index.php/features/178-eardrum-suck-the-mystery-solved)、[BGR](https://bgr.com/2141088/anc-pressure-explained/)、[RWTH Aachen](https://www.iks.rwth-aachen.de/en/news/colloquium/details/bachelor-presentation-investigations-on-suction-perception-with-anc-headphones/) |
| 一直塞着也会闷；调低降噪、摘下来歇会儿 | 入耳式耳塞长时间密封耳道、压迫耳道皮肤，会闷、热、潮（常识性描述，屏上不给数字）。 |

示意与简化：耳道画成直管（真实为 S 形）；波形画成横波线条（声音是纵波，空气点的前后挤压才是真实运动，片中两者同时画出）；慢放约 1 Hz 显示。
