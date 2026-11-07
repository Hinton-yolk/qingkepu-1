# FACTS · 戴着手套，为什么点不动屏幕？

| 说法（片中） | 依据 | 来源 |
|---|---|---|
| 手机屏幕下面是一张横竖两层的导电细线网（投射式电容屏） | 互电容方案：行、列两层电极叠在一起，中间隔一层薄绝缘，形成网格；控制芯片读每个交叉点的变化来定位 | [Nelson Miller: How does a projected capacitive touchscreen work](https://nelson-miller.com/how-does-a-projected-capacitive-touchscreen-work)；[Faytech: Capacitive touch screen basics](https://www.faytech.us/touchscreen-monitor/capacitive/capacitive-touch-screen-basics-how-it-works-types-explained/) |
| 手指一靠近，那一格的读数变小（「引走一点电」） | 手指通过人体接地，扰动两电极之间的电场，**互电容减小**。「引走一点电」是白话说法；准确说法是手指把一部分电场引走了 | [TI TIDUE90 · Mutual capacitance](https://ti.com/document-viewer/lit/html/TIDUE90/mutual-capacitance-t5367504-9) |
| 屏幕不管你按没按 | 电容屏感应的是导体靠近带来的电容变化，不是压力（压力式的是电阻屏，片中不提） | 同上 |
| 手套不导电，所以点不动 | 很多手套是绝缘材料，挡住手指和屏幕的电容耦合；**薄手套有时能用**，厚手套不行，所以片中只说「手套」，不说所有手套 | [USPTO 9836134](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/9836134)；[Nelson Miller: 5 myths](https://nelson-miller.com/5-myths-about-projected-capacitive-touchscreens) |
| 触屏手套在指尖织了导电线 | 触屏手套的指尖用导电纱线或导电材料 | [Nelson Miller: Everything you need to know](https://nelson-miller.com/everything-you-need-to-know-about-projected-capacitance-touchscreens) |
| 2010 年冬天，韩国有人拿香肠当触屏笔 | 2009–2010 年冬天寒潮，韩国 iPhone 用户用 CJ 的零食香肠戴着手套点屏幕；多家媒体报道。**销量涨四成的说法未核实，不用** | [The Register 2010-02-12](https://www.theregister.co.uk/2010/02/12/korean_sausage_stylus)；[Popular Science](https://www.popsci.com/technology/article/2010-02/meat-iphone-sausage-stylus) |
| 有的手机有「手套模式」 | 三星「触控灵敏度」：贴膜或戴手套时提高灵敏度；不是所有机型都有，厚手套仍可能不行。片中说「有的手机」 | [Samsung CA support](https://www.samsung.com/ca/support/mobile-devices/activate-touch-sensitivity-on-your-samsung-galaxy/)；[Samsung HK](https://www.samsung.com/hk_en/support/mobile-devices/is-it-possible-to-touch-the-device-while-wearing-gloves/) |

没有放进片子的：屏幕沾水会「乱跳」。资料说法不一致（TI 说水会产生和触摸方向相反的读数，另一些专利说接地的水滴会被当成触摸），先不讲。
