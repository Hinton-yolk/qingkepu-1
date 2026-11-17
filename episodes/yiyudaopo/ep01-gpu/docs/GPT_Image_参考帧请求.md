# 给导演：GPT Image 参考帧请求（Phase 2，可选）

只有一个镜头建议走「Blender 版式帧 → GPT Image 照片级首帧 → LTX」：**A 段数据中心冷通道（0:05.5–0:09.0）**。
理由：远景氛围镜头，细节对错不影响讲解，照片感带来的提升最大。MACRO / CHIP 是讲结构的镜头，器件不能被生成模型改动，继续用 Cycles。

## 输入帧（版式、机位、透视、灯位都以这两张为准）
- 首帧：`blender/out/DC/DC_0001.png`（1080×1920）
- 尾帧：`blender/out/DC/DC_0135.png`
- 相机：眼高约 1.45 m，28 mm（全画幅等效），沿冷通道中线往前推约 2.4 m，4.5 秒。

## 提示词（英文给 GPT Image，配上首帧）
```
Photorealistic vertical photo of a modern AI data center cold aisle, exactly matching the composition, camera height, lens and perspective of the attached layout frame.
Two rows of black 42U server racks face each other across a 1.8 m cold aisle. Each rack holds four 8U GPU servers with dark metal front bezels, large honeycomb air-intake grilles, a row of drive trays, silver pull handles and small blue/green status LEDs; 1U network switches at the top with dense cabling.
Grey raised-floor tiles (600 mm) with perforated tiles in the aisle. Overhead: wire-basket cable trays above each rack row with blue network cables, narrow yellow fiber raceways, linear white LED fixtures across the ceiling. A glass containment door at the far end of the aisle, softly lit from behind.
Cool, restrained lighting, realistic exposure, slight haze-free depth, shallow depth of field focused about 3 m ahead. No people, no logos, no text, no sci-fi glow, no particles, no lens flares.
```

## 不要改的地方（请在 GPT 结果里检查）
- 机柜数量、通道宽度、相机高度和消失点位置与版式帧一致（LTX 跟着灰模视频走，构图变了会穿帮）。
- 不加品牌标志、屏幕文字、人物。
- 光纤槽是黄色、细；不要变成横跨通道中间的大槽。
