# EP.10 实况照片 · FACTS（白话版 v1，2026-11-23）

来源等级：〔厂〕厂商资料；〔研〕厂商研究团队 / 论文；〔媒〕科技媒体；〔论〕论坛、用户实测；〔待〕还没找到可靠来源或只读到搜索摘要，进逐句脚本前要补。
本轮只读到搜索摘要，节点 ① 由审核用最强的模型对照原文核实。

| # | 片中说法 | 事实 | 来源 |
|---|---|---|---|
| 1 | 开了实况，按快门前后各留 1.5 秒 | iPhone 拍实况照片时，会把按下快门前后各 1.5 秒发生的事记下来；之后可以另选一帧作为主照片（key photo）、加效果或编辑 | 〔厂〕Apple 支持「Take and edit Live Photos」https://support.apple.com/HT207310 （〔待〕读原文摘原句） |
| 2 | 相机一打开就在拍，按之前那 1.5 秒平时不存，按了才留下 | 相机 app 打开时一直在取像，按快门之前那 1.5 秒只在按下后才保存，其余的丢掉 | 〔媒〕MacRumors「How to Use Live Photos on iPhone and iPad」https://www.macrumors.com/how-to/live-photos-iphone-ipad ；〔媒〕iPhone Life「How Live Photos Work—More Details Emerge」（转述苹果说法）（〔待〕找苹果一手说法） |
| 3 | 实况照片 = 按下那一刻的一张清楚照片 + 前后一小段视频 | 实况照片由一张全分辨率静态照片和一段短视频组成（文件上是一张 HEIC/JPEG 加一段 MOV） | 〔厂〕〔待〕Apple 开发者文档（PHLivePhoto）原句；〔论〕MacRumors 论坛「Live Photos … composed of separate JPG and MOV files」 |
| 4 | 转盘：新的一张进来，最老的被盖掉，只留最近一小段 | Google 相机：「一打开相机 app，就开始拍帧并存进一个环形缓冲区，不断擦掉旧帧给新帧腾地方」；Google 的开源示例 zsldemo 在预览的同时维护一个全尺寸帧的环形缓冲区，按下时从中挑一帧。苹果没有公开实况照片的内部实现，片中「转盘」是**示意**（逻辑上必须这样：按之前的画面要存在、又不能无限存） | 〔研〕Google Research「Night Sight: Seeing in the Dark on Pixel Phones」(2018) https://research.google/blog/night-sight-seeing-in-the-dark-on-pixel-phones/ ；〔研〕github.com/google/zsldemo |
| 5 | 不开实况，不少手机拍普通照片也从这一圈里拿刚拍好的，所以快门几乎没有延迟 | 零快门延迟（ZSL）：按下快门时，把缓冲区里最近的 9 或 15 帧交给 HDR+ 合成（Pixel）；HDR+ with Bracketing：快门前的取景帧就是用来合成的帧，再加按下后的一张长曝光。Android CameraX 提供 ZSL 拍照模式（环形缓冲区存最近几帧）。苹果 Deep Fusion：按快门前已拍好 8 张（4 张标准曝光、4 张短曝光），按下时再拍一张长曝光（媒体转述 2019 发布会）。各家实现不同 → 片中说「不少手机」，加注「示意」 | 〔研〕Google Research（同 #4）；〔研〕Google Research「HDR+ with Bracketing on Pixel Phones」(2021) https://research.google/blog/hdr-with-bracketing-on-pixel-phones/ ；〔厂〕Android Developers「Zero-Shutter Lag」https://developer.android.com/media/camera/camerax/take-photo/zsl ；〔媒〕Digital Trends（Deep Fusion，〔待〕找苹果一手说法） |
| 6 | 安卓多叫「动态照片」，时长各家不同 | 三星「动态照片」（Motion photo）：说明写快门前录几秒，S24 新闻稿写最多 3 秒预览，新机可选「快门前后」或「仅快门前」；vivo / OPPO / 华为的叫法和时长，中文网页说法互相矛盾（有写前后各 1.5 秒，也有写前 0.5 秒后 1 秒） | 〔厂〕Samsung 支持「Capture group shots with Motion photos」https://www.samsung.com/us/support/answer/ANS10004858/ ；〔厂〕Samsung Newsroom「Finally, a Mobile Camera That Ensures You Never Miss a Moment」；〔待〕国产各家官方说明（叫法：动态照片 / 实况照片） |
| 7 | 小提示：拍到闭眼，点编辑，换一帧当封面 | iPhone「照片」里可以给实况照片另选一帧作为主照片 | 〔厂〕Apple 支持（同 #1） |
| 8 | 小提示括号：换出来的那帧没有原图清楚 | 另选的主照片取自视频里的一帧，分辨率低于原来的静态照片（有用户报 iPhone X 从 4032×3024 降到 3662×2744）；只有论坛和用户实测，没有苹果官方说法 | 〔论〕Apple 社区「Live Photo Quality Loss When Changing Key Frame」https://discussions.apple.com/thread/250580900 ；〔论〕MacRumors 论坛；〔待〕可靠来源，补不到就把措辞改成「可能没原图清楚」 |
| 9 | （不进片，发布正文可用）长曝光效果 | iPhone 实况照片可加「循环播放」「来回播放」「长曝光」三种效果；长曝光把运动模糊开，模拟单反慢门 | 〔厂〕Apple 支持（同 #1）；iPhone 使用手册「Edit Live Photos」 |
| 10 | 一秒几十张（不写具体数） | 取景预览通常每秒 30 帧左右，各机型、模式不同，片中不写具体帧率 | 〔待〕 |
