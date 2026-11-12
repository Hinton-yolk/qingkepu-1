// 图里的固定用字（坐标轴、图例、图内小注等）。timeline.json 里没有这些字，集中放在这里，方便审核逐条核对。
// 镜头文案、角注、字幕、标签一律来自 timeline.json，不写在代码里。
// 这张表同时列在 remotion/README.md「图内固定用字」一节；改这里的字，也要改那张表。
export const STR = {
  // 占位卡
  placeholderTag: "占位 · 非成片画面",
  placeholderScale: "尺度",
  placeholderStatus: "状态",
  placeholderCamera: "相机",
  placeholderHint: "此处为 Blender 画面，尚未渲染",
  // 波形
  threshold: "判决门限",
  eye: "逐位叠起来看（眼图）",
  // 时序图
  timeAxis: "时间",
  /** 并行那一行标题后面的小字：图里并行线的条数（shotConfig.TIMING_LANES）和 3D 画面里的条数不一样，在图里说明 */
  timingLanes: (n: number) => `（图里只画 ${n} 条）`,
  // 读数
  offset: "偏移",
  approx: "约",
  spotFiber: "光纤能接住的范围",
  spotChip: "芯片来的光斑",
  percent: "%",
  unitMicron: "µm",
  // 路线图例（没有路线取样锚点时的退路）：两段之间的箭头
  arrow: "→",
};
