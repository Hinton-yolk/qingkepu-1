# 三条抖音拆解版口播（第五稿：科普 = 翻译）：python3 make_script.py → script_s1.json / s2 / s3
# 每句：id、text、sub（关键点字幕）、big（开头两句的同步字，贴在画面里的东西旁边）、seg、reuse（一字不差的旧录音）；SAY = TTS 用的读法
import json
S1 = [
 ('p01', '你发出去的每张照片，', None, '你发出去的每张照片，', 'open', None),
 ('p02', '在芯片之间都要跑一趟。', None, '在芯片之间都要跑一趟。', 'open', None),
 ('p02b', '你问 AI 的每个问题、发的每张照片，背后都是芯片之间在疯狂寄快递。这一条讲：快递为什么要排成一队寄。', None, None, 'open', None),
 ('p03', '直觉上，修几十条路，把照片切成几十条一起送，最快。', None, None, 'explain', None),
 ('p04', '慢的时候确实没问题：每一条都按时到，照片拼得严丝合缝。', None, None, 'explain', None),
 ('p05', '可速度一快，一张紧跟着一张；哪条路长了一点点，那一条就晚到半步，拼进了下一张。', None, None, 'reveal', None),
 ('p06', '照片就成了这样。', None, None, 'reveal', None),
 ('p07', '聊天、转账也一样：没有纠错的话，错一位，意思就全变了。', None, None, 'reveal', None),
 ('p08', '路越多，越难让每一条都一样长。', None, None, 'reveal', None),
 ('p09', '所以最快的芯片反过来：只修几条路，让数据排成一队，一个接一个跑。不用等谁，就能越跑越快。', None, None, 'reveal', None),
 ('p10', '一句话带走：', None, None, 'end', 'a19'),
 ('p11', '路少，反而不会乱。', None, None, 'end', None),
 ('p12', '下一条：排成一队以后，对面怎么知道数到了第几个？', None, None, 'end', None),
]
S2 = [
 ('q01', '少数一个 1，', None, '少数一个 1，', 'open', None),
 ('q02', '这句话就全乱了。', None, '这句话就全乱了。', 'open', None),
 ('q02b', '这一条讲快递签收：对面怎么一个不差地清点。', None, None, 'open', None),
 ('q03', '芯片之间每秒要数上千亿个 0 和 1。可线上连着五个 1，看起来就是一条直线：四个，还是五个？', None, None, 'open', None),
 ('q04', '没人在旁边打拍子，它怎么数清？', None, None, 'open', None),
 ('q05', '就像你跟着一首歌拍手：没人给你打拍子，你听着鼓点，自然就跟上了。', None, None, 'explain', None),
 ('q06', '芯片也一样：信号每跳一下，就是一个鼓点。它跟着鼓点校准自己，几下就踩准了。', None, None, 'reveal', None),
 ('q07', '踩准以后，每一拍看一眼：五个，不是四个。', None, None, 'reveal', None),
 ('q08', '可要是一长串全是 1，就像歌里拖了一个长音，没有鼓点，拍子就会慢慢跑偏。', None, None, 'reveal', None),
 ('q09', '所以发出去之前，先把数据打乱，让鼓点一直都在；收到以后，再还原回来。', None, None, 'reveal', None),
 ('q10', '一句话带走：', None, None, 'end', 'a19'),
 ('q11', '芯片数 0 和 1，靠的不是眼睛，是耳朵。', None, None, 'end', None),
 ('q12', '下一条：芯片说速度翻倍，该问哪三句？', None, None, 'end', None),
]
S3 = [
 ('k01', '发布会上的速度翻倍，', None, '发布会上的速度翻倍，', 'open', None),
 ('k02', '到手可能打对折。', None, '到手可能打对折。', 'open', None),
 ('k03', 'AI 芯片之间也在天天寄快递，速度动不动就翻倍。这一条讲：看到翻倍，先问哪三句。', None, None, 'open', None),
 ('k04', '第一句：在什么路上跑的？就像千兆宽带，到你卧室可能只剩一半。', None, None, 'explain', None),
 ('k05', '同样写着 224G，有的能推过一米长的铜缆，有的只跑几厘米。', None, None, 'explain', None),
 ('k06', '第二句：费不费电？就像手机，跑分越高，越容易烫手掉电。几万颗芯片一起跑，电费就是真金白银。', None, None, 'explain', None),
 ('k07', '第三句：真机测过没有？发布会上的续航，和你到手的续航，常常是两回事。', None, None, 'reveal', None),
 ('k08', '一句话带走：', None, None, 'end', 'a19'),
 ('k09', '下次看到速度翻倍，先问：什么路？费不费电？实测了吗？', None, None, 'end', None),
 ('k10', '下一条：信号上路以后，为什么会越跑越模糊？', None, None, 'end', 'z14'),
]
SAY = {'k05': '同样写着二百二十四G，有的能推过一米长的铜缆，有的只跑几厘米。'}
if __name__ == '__main__':
    for n, S in (('s1', S1), ('s2', S2), ('s3', S3)):
        json.dump([dict(id=i, text=t, sub=u, big=b, seg=g, reuse=r, say=SAY.get(i, t)) for i, t, u, b, g, r in S], open(f'script_{n}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(n, len(S), 'lines; new TTS bytes', sum(len(SAY.get(i, t).encode()) for i, t, u, b, g, r in S if not r))
