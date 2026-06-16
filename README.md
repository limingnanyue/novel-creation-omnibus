<div align="center">

# 🖋️ 小说创作全能工坊

> *「写小说很累？让Agent帮你写，但别让它替你结尾。」*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-novel--creation--omnibus-blueviolet)](SKILL.md)
[![skills.sh](https://skills.sh/b/limingnanyue/novel-creation-omnibus)](https://skills.sh/limingnanyue/novel-creation-omnibus)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Modules](https://img.shields.io/badge/Modules-19-green)](references/modules/)

**25套创作工具，一个Skill搞定。从黄金三章到通感痛觉，从番茄爆文到白描克制。**

[看效果](#它能做什么) · [安装](#快速开始) · [触发方式](#25个场景一键直达) · [它和同类有什么不同](#它和同类有什么不同) · [安全边界](#安全边界)

</div>

---

> **事情是这样的**：你脑子里有一个好故事，坐在电脑前，敲了两行字——删了。又敲了三行——又删了。
>
> 不是你不会写，是你得同时管节奏、人设、伏笔、钩子、字数、番茄标准、对话密度、去AI味、还有别让章首出现"第二天"。
>
> 所以我把25种创作工具塞进一个Skill里，你说"写第X章"它就跑长篇流程，说"发刀"它就翻虐心模板，说"去AI味"它就六门禁全开。**不是你一个人对着空白文档，是25个编辑坐在你旁边。**

---

## 它能做什么

| 你遇到的场景 | 它马上变成 |
|:------------|:-----------|
| 不知道第5章怎么写 | 📝 长篇正文6步流程：读状态→写→优化→同步→审计 |
| 写了3000字一股AI味 | ✨ 六门禁+三刀流+分级检测报告 |
| 想发刀但不知道怎么写才痛 | 💔 六种BE模板+刀力评分+三段式递进 |
| 想写番茄爆文 | 🚀 标题公式+八步法+数据评级 |
| 断更一个月了 | 🔄 4步恢复上下文，秒回状态 |

完整能力见 [19个模块索引](SKILL.md#-模块索引)。

---

## 快速开始

```bash
npx skills add limingnanyue/novel-creation-omnibus -g
```

装完对Agent说：

```text
写小说
```

或者更具体：

```text
写第3章，系统流，主角刚穿越。接上章结尾：他睁眼发现自己躺在一间破庙里。
```

---

## 25个场景一键直达

| 你想写什么 | 对Agent说 |
|:-----------|:----------|
| 长篇正文 | "写第X章" |
| 黄金三章 | "写个黄金三章开篇" |
| 短篇BE | "写短篇，3000字，BE" |
| 番茄爆文 | "写番茄爆款标题+导语" |
| 发刀虐心 | "发刀，日常化死亡" |
| 通感痛觉 | "写痛，被孤立的痛" |
| 去AI味 | "去AI味，中度处理" |
| 做大纲 | "做个大纲，重生商战题材" |
| 做人设 | "设计一个反派" |
| 搭世界观 | "搭世界观，修仙+科技" |
| 续写 | "接上文" |
| 断更重启 | "好久没写了" |
| 质检 | "检查这章有没有OOC" |
| 修衔接 | "修衔接，两章之间太跳" |
| 白描克制 | "白描，写一个母亲的故事" |
| 玩梗 | "加几个热梗" |
| 同人二创 | "写个AU，OOC检测" |

完整路由表见 [SKILL.md → 任务路由表](SKILL.md#-任务路由表)。

---

## 它和同类有什么不同？

| 维度 | 其他写作Skill | **本工坊** |
|:-----|:-------------|:-----------|
| 覆盖范围 | 单一写作类型 | 长篇/短篇/爆文/白描/同人/虐心全包 |
| 去AI味 | 简单替换禁用词 | 六门禁+三刀流+八类必查+分级检测报告 |
| 通感痛觉 | 无 | **全网独一份**：六大原型+意象库+三段式递进 |
| 质量门控 | 写完了事 | 写→审→改→检→锁稿 5阶段闭环 |
| 架构 | 单文件巨无霸 | **模块化路由**：按需加载，token友好 |
| 测试验证 | 无 | 8个测试用例，覆盖全部核心模块 |

---

## 安全边界

- ❌ 不会自动修改你的细纲/大纲/人设文件
- ❌ 不会在不确认的情况下删除任何内容
- ❌ 不会把小说内容写入公开文件
- ✅ 每次写正文前都会读取最新状态文件
- ✅ 所有关键决策（人物命运、剧情转折）等你确认

---

## 文件结构

```
novel-creation-omnibus/
├── SKILL.md                  # 主路由（路由表+冲突裁决+安全边界）
├── README.md                 # 安装说明与展示
├── LICENSE                   # MIT
├── examples/test-prompts.json # 8个测试用例
├── scripts/                  # 实用工具（待补充）
├── assets/                   # 截图/GIF（欢迎贡献）
└── references/modules/       # 19个独立模块
```

---

## 验证与测试

装完用这句验收：

```text
写个短篇BE，3000字，核心意象用伞。
```

合格的表现：它先读取短篇模块的规则，给出字数结构公式、核心意象贯穿法、结尾模板，然后输出3000字正文，章末有刀点。

---

## 致谢

- 内容方法论来源于真实网文创作实践
- 反AI味门禁受 [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) 启发
- 模块化架构参考 [Chinese-WebNovel-Skill](https://github.com/Tomsawyerhu/Chinese-WebNovel-Skill)
- 打磨报告由 [鲁班 | Luban](https://github.com/LearnPrompt/luban-skill) 生成
- [LearnPrompt](https://github.com/LearnPrompt) 系列技能生态

## License

[MIT](LICENSE)

---

<div align="center">

**写小说，一个工坊就够了。**

</div>
