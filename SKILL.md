---
name: novel-creation-omnibus
description: >
  小说创作全能工坊——从网文长篇到短篇故事，从番茄爆文到白描克制，从发刀虐心到通感痛觉，从大纲细纲到质量门控，一站式搞定。触发词包括但不限于：全流程、创作、写小说、写长篇、写短篇、一条龙、开始写、写章节、写正文、写细纲、续写、搭世界观、做人设、发刀、玩梗、去AI味、润色、修衔接、因果分析、全检、状态追踪、断更重启、黄金三章、爽文开头、系统流、番茄爆文、群像、众生相、网文生产、锁稿、审稿、通感痛、白描、克制写作、反差塑造、留白、现实主义。
  负触发（不要用于）：不要用于从零创建非小说类写作技能（用writing-skills）；不要用于代码注释或技术文档写作（用code-writing）；不要用于诗歌/歌词创作（用creative-writing）；不要用于翻译任务（用translation-skill）。
triggers:
  - 全流程
  - 创作
  - 写小说
  - 写短篇
  - 写长篇
  - 一条龙
  - 开始写
  - 写作
  - 写章节
  - 写正文
  - 写细纲
  - 续写
  - 搭世界观
  - 做人设
  - 发刀
  - 玩梗
  - 去AI味
  - 润色
  - 修衔接
  - 因果分析
  - 全检
  - 状态追踪
  - 断更重启
  - 黄金三章
  - 爽文开头
  - 系统流
  - 番茄爆文
  - 群像
  - 众生相
  - 网文生产
  - 锁稿
  - 审稿
  - 通感痛
  - 白描
  - 克制写作
  - 反差塑造
  - 留白
  - 现实主义
  - 写痛
  - 扎心
version: 5.3
last_updated: 2026-06-16
---

# 小说创作全能工坊 🖋️

> **写小说，从0到完本，一个Skill搞定。**
> 长篇网文、短篇虐文、番茄爆文、白描写作——25套创作工具，按需加载，即用即走。

---

## 🚨 总纲铁律（6条）

```
① 不加载外部技能——所有模块已内嵌在 references/modules/ 中
② 先通过路由表判定任务类型，再跳对应模块
③ 写作前必须确认：连续性规则+DS优化+去AI味+番茄标准+细纲读取
④ 流程必须走完，不得跳过任何步骤
⑤ 冲突看裁决表（conflict-fusion模块），不自作主张
⑥ 写完必须自检，不过不交差
```

---

## 📋 任务路由表

| 用户说 | 加载模块 |
|:-------|:---------|
| "写第X章" / "写下一章" | `core-writing` |
| "黄金三章" / "爽文开头" | `golden-three` + `core-writing§1.2` |
| "续写" / "接上文" | `core-writing§1.5（简化版）` |
| "写细纲" / "写章纲X" | `planning§2.2` |
| "搭世界观" | `world-characters`（第3章部分） |
| "做人设" / "反派" / "设计角色" | `world-characters`（第4章部分）|
| "群像" / "众生相" | `world-characters§4.9` |
| "做大纲" / "规划剧情" | `planning` |
| "写短篇" / "短故事" | `short-stories` |
| "发刀" / "虐文" / "BE" | `angst-writing` |
| "玩梗" / "加梗" | `memes-trends` |
| "去AI味" / "润色" | `anti-ai-polish` |
| "修衔接" | `transitions-causality` |
| "因果分析" / "逻辑检查" | `transitions-causality` |
| "查状态" / "更新台账" / "伏笔" | `state-tracking` |
| "结构设计" / "质检" | `quality-control` |
| "同人" / "二创" / "OOC" | `fan-fiction` |
| "网文生产" / "锁稿" / "审稿" | `production-line` |
| "快速档/标准档/深度档" | `adaptive-scheduling` |
| "系统流" / "番茄爽文" | `viral-writing§16.3` |
| "爆文" / "番茄爆款" | `viral-writing` |
| "白描" / "克制写作" | `restrained-writing`（第17章）|
| "平庸" / "现实向" | `restrained-writing`（第18章）|
| "断更重启" | `resume-skill-creation` |
| "创技能" / "新技能" | `resume-skill-creation` |
| "仪表盘" / "进度" | `adaptive-scheduling§15.6` |
| "写痛" / "通感痛" / "扎心" | `pain-synaesthesia` |
| "热梗" / "更新仓库" | `memes-trends` |
| 模糊指令 | 追问 |

---

## 📦 模块索引

所有模块文件位于 `references/modules/`，按需加载即可。

| 模块 | 文件 | 内容 | 适用场景 |
|:-----|:-----|:-----|:---------|
| 📝 长篇正文 | `core-writing.md` | 6步流程：读取状态→写正文→优化→同步→每5章更新→每10章因果 | 日常写章节 |
| 📐 大纲与细纲 | `planning.md` | 总大纲模板+单章细纲+文件管理+9维全检 | 规划剧情 |
| 🏛️ 世界观与人物 | `world-characters.md` | 八维世界观+五维人物骨架+群像引擎+反派设计+跨卷弧光 | 搭设定、做人设 |
| 📖 短篇故事 | `short-stories.md` | 字数结构+黄金开篇+人物三维+冲突升级+核心意象+结尾七选一 | 写短篇 |
| 💔 虐心写作 | `angst-writing.md` | 日常化死亡+开放式BE+人设反转+刀力评分+节奏铁律 | 发刀、BE |
| 🔥 玩梗与热梗 | `memes-trends.md` | 梗分类+融入技法+热梗仓库管理+6小时更新规则 | 搞笑、沙雕 |
| ✨ 去AI味 | `anti-ai-polish.md` | 六大门禁+三刀流+八类必查+分级处理+检测报告 | 润色、改文 |
| 🔗 衔接与因果 | `transitions-causality.md` | 断裂等级修复+水文处理+因果链分析+信息差分析 | 修衔接、逻辑检查 |
| 📊 状态追踪 | `state-tracking.md` | 上下文追踪+记忆台账+伏笔管理+对话记忆 | 查状态、追伏笔 |
| ✅ 质量门控 | `quality-control.md` | 体量适配+三层质检（字词/句段/篇章） | 质检、错别字 |
| 🎭 同人创作 | `fan-fiction.md` | 同人6阶段+OOC量化评分+历史考据+读者模拟 | 二创、AU |
| 🏭 网文生产 | `production-line.md` | 14节点生产流程+反方审稿+锁稿6条件 | 锁稿、审稿、交接 |
| ⚡ 自适应调度 | `adaptive-scheduling.md` | 三档切换+6种触发检测+仪表盘+执行预览 | 快速/标准/深度档 |
| 🚀 番茄爆文 | `viral-writing.md` | 平台认知+标题公式+导语模板+八步法+脑洞+数据评级 | 爆款、系统流 |
| 🖋️ 白描与平庸 | `restrained-writing.md` | 双线叙事+反差塑造+物象象征+留白克制+细节定锚+代际叙事 | 白描、现实向 |
| 🔄 断更与技能创建 | `resume-skill-creation.md` | 断更4步恢复+技能创建流程 | 断更重启、创技能 |
| 🏆 黄金三章 | `golden-three.md` | 三章逐章标准+字数完读率目标 | 爽文开头 |
| ⚖️ 冲突裁决与三法融合 | `conflict-fusion.md` | 跨规则冲突裁决+爽文/白描/平庸三法融合对照表 | 规则冲突、多法融合 |
| 🌊 通感痛觉描写 | `pain-synaesthesia.md` | 通感四式+六大原型+三段式递进+剂量管控+意象库+多题材适配 | 写痛、扎心、隐痛 |

---

## ⚖️ 跨规则冲突裁决

```
对话占比≥50% vs 标签≤40% → 多用动作穿插，对话≥40%
句号≤30% vs 短句快节奏 → 短句用逗号+破折号
爽点密度 vs 剧情推进 → 爽点服务于剧情
世界观 vs 剧情需要 → 世界观优先
去AI味 vs 角色风格 → 角色风格优先（口头禅不可删）
HE+三级刀 → HE只能用微小缺口
OOC vs AU自由 → AU内标注后允许
考据 vs 创作自由 → 强制标注AU/架空
白描留白 vs 爽文钩子 → 按题材选，可融合
平庸不解决 vs 爽文打脸 → 按题材选
快速档 vs 深度质检 → 按章节分类自动选档
系统流短章 vs 通用2000字 → 按任务类型选标准
三笔活人 vs 五维骨架 → 生态层用三笔，核心层用五维
白描法 vs 爽文法 → 开篇爽文→中段白描→结尾催泪可融合
平庸书写 vs 虐心写作 → 平庸写日常磨损，虐心写戏剧破碎
通感痛觉 vs 虐心写作 → 通感痛觉写日常隐痛，虐心写作写戏剧大悲，可递进联动
```

---

## 🛡️ 安全边界

- **不动源文件**：写作前必须读取状态文件，但不覆盖/删除用户原始数据
- **不自作主张**：所有关键决策（大纲方向、剧情转折、人物命运）必须等用户确认
- **不泄露隐私**：不将用户的小说内容、人设、世界观写入公开文件
- **不越权操作**：不自动删除/修改用户已有的创作文件
- **断更重启不破坏上下文**：只读取和恢复，不清空任何已有数据

---

## 📂 文件结构

```
novel-creation-omnibus/
├── SKILL.md                          # 主路由文件（任务调度+模块索引）
├── README.md                         # 安装说明与展示
├── LICENSE                           # MIT
├── SKILL.backup.md                   # 原始完整版（v5.2备份）
├── examples/
│   └── test-prompts.json             # 测试用例
├── assets/                           # 截图/GIF（待补充）
└── references/modules/
    ├── core-writing.md               # 长篇正文写作
    ├── planning.md                   # 大纲与细纲
    ├── world-characters.md           # 世界观与人物
    ├── short-stories.md              # 短篇创作
    ├── angst-writing.md              # 虐心写作
    ├── memes-trends.md               # 玩梗与热梗
    ├── anti-ai-polish.md             # 去AI味
    ├── transitions-causality.md      # 衔接与因果
    ├── state-tracking.md             # 状态追踪
    ├── quality-control.md            # 质量门控
    ├── fan-fiction.md               # 同人创作
    ├── production-line.md            # 网文生产
    ├── adaptive-scheduling.md        # 自适应调度
    ├── viral-writing.md              # 番茄爆文
    ├── restrained-writing.md         # 白描与平庸
    ├── resume-skill-creation.md      # 断更与技能创建
    ├── golden-three.md               # 黄金三章
    ├── conflict-fusion.md            # 冲突裁决与三法融合
    └── pain-synaesthesia.md          # 通感痛觉描写
```
