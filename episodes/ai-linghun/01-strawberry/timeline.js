// timeline.js — the single source of truth for picture (index.html) and, later, sound.
// 「AI 灵魂拷问」EP.01 为什么 AI 数不清 strawberry 里有几个 r？ — DRAFT (no voice yet).
// Timing is estimated from the narration at the Fish Audio「科普」voice's measured pace (config/voice.md: 5.3–6.2 字/秒;
// we use 5.85). Once the voice is generated, replace EST with the measured clip lengths and every cue follows.
(function (root) {
  const FPS = 30, W = 1080, H = 1920;
  const CPS = 5.85;              // characters per second (Fish「科普」, 光互连 measured 5.85–6.2)
  const GAP = 0.22, STOP = 0.32; // pause after a clause / after a full stop

  // narration, one entry per voice clip. hold = extra seconds after a line before the next one (the caption stays up).
  // seg = which scene it belongs to. [ ] marks the key word: the caption shows it in coral,
  // at the moment the picture shows the same thing in coral (the voice reads the text without the brackets: use .plain).
  const LINES = [
    // A · hook (first frame: the chat with the wrong answer + the big question)
    { seg: "A", text: "AI 不按字母读。", dur: 1.4700854700854702 },   // 用户 11-22 要求改写原句「AI 根本“看不见”字母。」（三轮观众都卡在「它明明能打出 strawberry」）；措辞由主 agent 拟，待用户确认。dur = 原句的估算时长，后面的画面、配乐、音效逐帧不动
    { seg: "A", text: "问它 strawberry 里有几个 r，它曾经很自信地说：[两个]。" },
    { seg: "A", text: "正确答案是[三个]。" },
    { seg: "A", text: "如今很多 AI 已经能答对，" },
    { seg: "A", text: "可它当初为什么会错？" },
    // B · letters vs blocks
    { seg: "B", text: "我们[一个字母一个字母]地看，", hold: 0.3 },
    { seg: "B", text: "AI 却先把它切成一块一块的“[积木]”。", hold: 0.6 },
    { seg: "B", text: "strawberry 在它眼里，可能就是 [str、aw、berry] 三块；", hold: 1.1 },
    { seg: "B", text: "放进句子里，整个词甚至只是[一块]。", hold: 0.9 },
    { seg: "B", text: "这种积木，行业里叫 [Token]。", hold: 0.5 },
    // C · the chain-word player
    { seg: "C", text: "AI 说话也是[一块一块]往外接的，" },
    { seg: "C", text: "它本质上就是一个读遍了整座图书馆的“[接龙高手]”。" },
    // D · the phone-call analogy + Chinese
    { seg: "D", text: "问它有几个 r，就像你在电话里听到一个人的名字，" },
    { seg: "D", text: "对方突然问：我的名字一共[几笔]？" },
    { seg: "D", text: "你认识这个名字，却从没“[看见]”过它。" },
    { seg: "D2", text: "中文也一样，常见的词可能整个就是[一块]积木，" },
    { seg: "D2", text: "生僻字反而会被拆成[碎块]。" },
    // E · why not letter by letter
    { seg: "E", text: "那为什么不一个字母一个字母地读？" },
    { seg: "E", text: "因为[太慢、太贵]。" },
    { seg: "E", text: "按字母读，一句话的长度要[翻好几倍]，" },
    { seg: "E", text: "而 AI 每多读一块积木，就要多算[一大笔账]。" },
    // F · one block → numbers → the chip (shortened 2026-11-22: the audience wanted to get back to the strawberry sooner)
    { seg: "F", text: "这笔账有多大？" },
    { seg: "F", text: "每块积木都会被换成[几千个数字]，" },
    { seg: "F", text: "芯片里几十万个小工人，同时做[乘法和加法]。" },
    { seg: "F", text: "每读一块积木，大约要算[两千亿次]；" },
    { seg: "F", text: "你随口问一句，就是[几万亿次]运算。" },
    { seg: "F", text: "这些小工人住的地方，就是 [GPU]。" },
    // G · back up: the punchline
    { seg: "G", text: "所以 AI 不是笨，是它看世界的“[最小单位]”和我们不一样。" },
    { seg: "G", text: "很多时候我们觉得别人“连这都不会”，" },
    { seg: "G", text: "也许只是他看世界用的[积木]，和你不同。" },
    // H · next episode
    { seg: "H", text: "既然 AI 只是在一块一块地猜积木，" },
    { seg: "H", text: "它会不会猜错，而且错得[理直气壮]？" },
    { seg: "H", text: "下期聊：AI 为什么会一本正经地胡说八道。" },
  ];

  // how long the voice takes to say a line: CJK characters count 1, Latin words by syllables, punctuation adds a breath.
  const LATIN = { AI: 1.6, strawberry: 3.2, r: 1, str: 2.4, aw: 1.4, berry: 2, Token: 2, GPU: 3 };
  function est(text) {
    let u = 0;
    for (const w of text.match(/[A-Za-z]+/g) || []) u += LATIN[w] ?? Math.max(1, w.length / 2.5);
    u += (text.match(/[一-鿿]/g) || []).length;
    const commas = (text.slice(0, -1).match(/[，、；：]/g) || []).length;
    return u / CPS + commas * 0.12;
  }
  const L = []; let t = 0;
  for (const ln of LINES) {
    const d = ln.dur ?? est(ln.text);   // dur: fixed length (keeps everything after it where it was)
    L.push({ ...ln, plain: ln.text.replace(/[\[\]]/g, ""), t0: +t.toFixed(2), t1: +(t + d).toFixed(2) });
    t += d + (/[。？]$/.test(ln.text) ? STOP : GAP) + (ln.hold || 0);   // hold: extra time after the line for the picture to finish (user 11-22: 12–24 s a little too fast)
  }
  const END_CARD = +(L[L.length - 1].t1 + 0.4).toFixed(2);
  const DUR = +(END_CARD + 3.2).toFixed(2);

  const TL = { FPS, W, H, CPS, LINES, L, est, END_CARD, DUR };
  if (typeof module !== "undefined" && module.exports) module.exports = TL;
  else root.TL = TL;
})(typeof window !== "undefined" ? window : globalThis);
