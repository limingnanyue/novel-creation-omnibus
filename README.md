<div align="center">

# 🖋️ 小说创作全能工坊 v10.0

> *「写小说最难的不是写，是写完不烂尾、不水、不带AI味。」*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-10.0-blueviolet)](SKILL.md)
[![skills.sh](https://skills.sh/b/limingnanyue/novel-creation-omnibus)](https://skills.sh/limingnanyue/novel-creation-omnibus)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Modules](https://img.shields.io/badge/Modules-46-brightgreen)](references/modules/)
[![AI 去味](https://img.shields.io/badge/AI%E5%8E%BB%E5%91%B3-L1--L4%E5%9B%9B%E5%B1%82%E7%A1%AC%E9%97%A8%E7%A6%81%E2%9C%A8-orange)](references/modules/anti-ai-polish.md)
[![Audit](https://img.shields.io/badge/Audit-E1--E5%E4%BA%94%E4%B8%93%E5%AE%B6-red)](references/modules/audit-workflow.md)
[![SkillOpt](https://img.shields.io/badge/SkillOpt-v0.2.0%20%E8%87%AA%E8%BF%9B%E5%8C%96-9cf)](references/modules/skill-evolution.md)
[![Sleep](https://img.shields.io/badge/Sleep-%E5%A4%9C%E9%97%B4%E7%A6%BB%E7%BA%BF%E8%87%AA%E8%BF%9B%E5%8C%96-6f42c1)](references/modules/sleep-evolution.md)
[![Meta](https://img.shields.io/badge/Meta-%E5%A4%9A%E7%9B%AE%E6%A0%87%E5%B8%95%E7%B4%AF%E6%89%98-d63384)](references/modules/meta-optimizer.md)
[![Compaction](https://img.shields.io/badge/Compaction-%E5%8E%8B%E7%BC%A9%E6%94%B6%E6%95%9B%7C8k%20token%E9%83%A8%E7%BD%B2-198754)](references/modules/skill-compaction.md)

**从0到完本，46套工具按需加载——长篇网文、短篇虐文、番茄爆文、白描克制、五专家审计、技能自进化、夜间离线自进化、多目标元优化、自适应技能压缩，一个工坊搞定。**

[看效果](#效果示例) · [安装](#快速开始) · [触发方式](#触发方式) · [46个模块](#46个模块按需加载) · [它和同类有什么不同](#它和同类有什么不同) · [安全边界](#安全边界) · [验证与测试](#验证与测试)

</div>

---

## 效果示例

![demo](assets/demo.gif)

> 上图为脚本真实运行录屏（3帧循环）。完整章节示例见 [examples/sample-chapter.md](examples/sample-chapter.md)，工具输出见 [examples/demo-output.md](examples/demo-output.md)。

**输入：** "写夜班出租车司机接到一单去殡仪馆的女孩，要克制白描，不留AI味"

**输出节选：**

```
标题：《夜班最后一单》

第一章

烟灰缸满了。

老周把车停在路边，下车倒了倒。风一吹，烟灰扑脸上，他咳了两声。

凌晨两点四十。环城高速上就他一辆车。

手机响了。拼车单，目的地城西殡仪馆。

他愣了一下，接了。

上车的是个女的，二十出头，白裙子，头发湿着。

"师傅，走高速。"

"殡仪馆这会儿不开门。"

"我知道。"
```

<sub>↑ 章首"烟灰缸满了"无时间词；300字内入题；零 em-dash、零"像"字比喻、零 AI 意象；对话不完整（"我知道。"）；真人门检命中（具体细节：零三年刀疤/八年/小卖部）——过 L1-L4 四层硬门禁</sub>

---

## 快速开始

```bash
# 一行安装
npx skills add limingnanyue/novel-creation-omnibus -g
```

装完直接对 Agent 说：

```text
写小说
```

## 触发方式

| 你想做什么 | 对 Agent 说 |
|:-----------|:----------|
| 写正文 | "写第X章，接上章结尾" |
| 搭世界观 | "搭一个修仙世界的世界观" |
| 做人设 | "设计一个反派" |
| 写对话 | "帮我优化这段对话，加潜台词" |
| 开篇钩子 | "帮我写个第一章开头，要抓人" |
| 去AI味 | "去AI味，我是用Claude写的" |
| 写短篇 | "写个短篇BE，3000字" |
| 规则怪谈 | "写个规则怪谈，办公室题材" |
| 模型优化 | "针对DeepSeek优化我的写作策略" |
| 读者心理 | "分析我这章的读者留存问题" |
| 断更重启 | "好久没写了，帮我恢复" |
| 动作描写 | "帮我写一段打斗，三拍式节奏" |
| 多线叙事 | "帮我设计三条线的交织节奏" |
| 世界体系 | "设计一个修仙力量体系" |
| 修改初稿 | "帮我改一下这章，4层流程" |
| 氛围渲染 | "这一段要压抑氛围" |
| 市场分析 | "这个题材选哪个平台好" |
| **专家审计** | "审计这章，五专家会诊" |
| **风格配置** | "给这本书定个调，都市商战电影感档" |
| **逐句审查** | "对这章逐句审查，电报体/解说腔都查" |
| **节拍审计** | "查这章在 Dramatica 11 拍的什么位置" |
| **伏笔对账** | "对账伏笔库，有失约的吗" |
| **MBTI 声线** | "按 INTJ 给主角定对白声线" |
| **技能自进化** | "训练技能，跑一个 epoch 自进化" |
| **夜间自进化** | "跑一次 sleep，夜间巩固技能" |
| **多目标优化** | "跑多目标帕累托，看四维前沿" |

完整触发词列表见 [SKILL.md](SKILL.md) 路由表。

## 你什么时候需要它？

- **写长篇网文**：日更2000-2500字/章，章章有钩子，自动追踪状态
- **写番茄爆文**：标题公式+导语模板+八步法+数据评级+系统流特化
- **写黄金开头**：12种爆款开篇+300字生死线自检+章末钩子4型
- **写对话**：语速4档+潜台词3级+声线5维+群像管理+**MBTI 16型对白声线档案**
- **写虐心BE**：六大原型痛觉+刀力评分+三段式通感递进+开放式BE
- **去AI味**：**L1-L4 四层硬门禁**+L3方法论三节+6类逐句审查判据+段落功能二分法+DeepSeek 734句式黑名单
- **写规则怪谈/无限流/直播文/末世/悬疑/种田**：各题材独立模板
- **断更重启**：4步恢复上下文+连载管理策略+读者留存方案
- **针对不同模型优化写作**：Claude/DeepSeek/GPT/Qwen/Kimi/豆包各分支策略
- **让文字更有味道**：五感缺失检测+口语化六法+小动作体系+食物描写
- **设计人物弧光**：正向弧7阶段+负向弧5阶段+关系弧+多人物弧交织
- **管理长篇连载**：存稿策略+滚动大纲+断更恢复4步+读者留存策略
- **适配平台规则**：起点/飞卢/晋江三大平台写作标准+签约门槛+跨平台改编
- **设计情绪高潮**：燃/泪/甜/震四类高潮+七步结构+**语言温度词库（8类热词+微表情库）**
- **生成创作灵感**：8种灵感生成法+30个情节模板+灵感仓库管理
- **理解读者心理**：情绪闭环+代入感三要素+弃书TOP10对策+情绪仪表盘
- **写动作/环境/外貌/战斗**：三拍式动作节奏+环境五感矩阵+战斗三秒规则+细节具象化
- **多线叙事**：POV切换策略+多线交织3种结构+**16维事实快照+三库协同**
- **控制节奏**：快慢交替公式+情节密度曲线+读者疲劳管理+长短章交替
- **设计世界体系**：力量等级+经济系统+政治格局+社会阶层+组织设计
- **修改工作流**：4层修改(结构→章节→句子→校对)+打乱重排+七刀精修
- **管理副线**：四大副线类型+主副线比例+收束时机+支线轮换
- **渲染氛围**：五种基础氛围+构建三阶段+三叠法+氛围反转
- **市场战略**：平台分析+读者画像+差异化定位+竞争分析+IP评估
- **专家审计**：五专家面板(E1-E5)+11维评估+6阶段流程+交叉审计+评分治理红线
- **定调与风格统一**：8风格维度+7题材路由+8典型档位+风格漂移检测
- **剧情结构审计**：Dramatica 11拍节拍+节拍×伏笔×角色协同矩阵+钩子真假4维判定+伪因果判定

## 它会交付什么？

- ✅ **完整的章节正文**（长篇2000-2500字/番茄爽文1200-1500字）
- ✅ **AI味检测报告**（L1-L4四层硬门禁+逐句审查+段落功能二分法+模型专属修正）
- ✅ **状态追踪档案**（16维事实快照+人物位置/伤势/好感度/伏笔/情绪曲线）
- ✅ **因果链分析报告**（起因→因果链→人物信息差→章节功能）
- ✅ **刀力评分**（6大痛觉原型+通感四式/剂量管控/三段式递进）
- ✅ **对话声线档案**（每个角色专属说话方式+潜台词设计+**MBTI 16型声线**）
- ✅ **场景卡片**（目标/冲突/变化/进出/衔接一致性检查）
- ✅ **人物弧光规划**（起点→关键转折→终点的变化路径）
- ✅ **描写提升报告**（动作/环境/外貌/战斗等维度改进建议）
- ✅ **节奏分析**（密度曲线+疲劳点+长短章优化建议）
- ✅ **修改审计**（修改层次/删除比例/读者反馈整合状态）
- ✅ **五专家审计报告**（E1语感/E2剧情/E3人物/E4一致性/E5商业 + 11维加权评分 + 主要矛盾标注）
- ✅ **风格档案**（style_config.json 8维度配置 + 风格漂移检测结果）
- ✅ **伏笔状态机报告**（active/recalling/resolved/broken/dropped 5态 + 硬指标预警）
- ✅ **节拍审计报告**（Dramatica 11拍定位 + 节拍×伏笔×角色协同检查）
- ✅ **跨会话状态文件**（meta_review_log.jsonl + next_focus 注入）

## 46个模块，按需加载

| 模块 | 说明 |
|:-----|:-----|
| `core-writing` | 长篇正文6步流程 |
| `planning` | 大纲模板+细纲+9维全检 |
| `world-characters` | 世界观+人物五维+群像引擎 |
| `short-stories` | 短篇字数结构+结尾七选一 |
| `angst-writing` | 日常化死亡+刀力评分 |
| `memes-trends` | 玩梗六类+热梗仓库 |
| `anti-ai-polish` | **L1-L4四层硬门禁+L3方法论三节+6类逐句审查+段落功能二分法+DeepSeek 734句式** |
| `transitions-causality` | 衔接修复+因果链 |
| `state-tracking` | **三库协同+5态伏笔状态机+跨会话状态机** |
| `quality-control` | 三层质检 |
| `fan-fiction` | 同人六阶段+OOC量化 |
| `production-line` | 14节点生产+锁稿 |
| `adaptive-scheduling` | 三档切换+仪表盘 |
| `viral-writing` | 番茄爆文八步法+数据评级 |
| `restrained-writing` | 白描双线叙事+平庸现实 |
| `golden-three` | 黄金三章标准+完读率 |
| `conflict-fusion` | 跨规则裁决+三法融合 |
| `pain-synaesthesia` | 通感四式+六大原型（900行） |
| `model-optimization` | **6大模型分支策略** |
| `new-genres` | **规则怪谈/无限流/直播/末世/悬疑/种田** |
| `flavorful-writing` | **五感+口语化+小动作+食物** |
| `dialogue-mastery` | **对话8大功能+声线5维+潜台词+MBTI 16型对白声线档案** |
| `opening-hooks` | **12种爆款开篇+章末钩子4型** |
| `plot-engineering` | **番茄循环+反转7式+冲突6级+Dramatica 11拍+钩子真假4维+伪因果判定+节拍×伏笔×角色协同矩阵** |
| `reader-psychology` | **情绪闭环+弃书TOP10对策** |
| `scene-crafting` | **场景四要素+6大场景类型+衔接** |
| `character-arcing` | **正向弧7阶段+负向弧+关系弧** |
| `serial-management` | **存稿策略+断更恢复+读者留存** |
| `platform-rules` | **起点/飞卢/晋江三大平台规则** |
| `emotional-climax` | **燃/泪/甜/震四类高潮+七步结构+语言温度词库（8类热词+微表情库）** |
| `idea-generator` | **8种灵感法+30个情节模板** |
| `descriptive-craft` | 描写技法：动作三拍/环境五感/战斗三秒 |
| `narrative-weaving` | **多线叙事：POV切换/三结构/线索铺设+三库协同+5态伏笔状态机+16维事实快照+跨会话状态机** |
| `pacing-dynamics` | 节奏动力学：密度曲线/疲劳管理/长短章交替 |
| `world-systems` | 世界运转体系：力量等级/经济/政治/社会 |
| `revision-workflow` | 修改工作流：4层修改/重排法/七刀精修+8类CT一致性检查 |
| `subplot-craft` | 副线编织法：四大副线/主副比例/收束时机 |
| `atmosphere-mood` | 氛围渲染术：五种氛围/三叠法/反转手法 |
| `market-strategy` | 市场战略：平台分析/读者画像/IP评估 |
| `audit-workflow` | 🔍 **五专家面板(E1-E5)/11维评估/6阶段流程/交叉审计/跨会话状态机/评分治理红线P0/预算护栏/完整专家schema** |
| `style-configuration` | 🎨 **v6.2：8风格维度+7题材路由+8典型档位+风格漂移检测+题材×11维评估器权重调整** |
| `skill-evolution` | 🧬 **v7.0：SkillOpt六步循环(Rollout→Reflect→Aggregate→Select→Update→Evaluate)+EditOp有界编辑+验证门+学习率预算+拒绝编辑缓冲+best_skill版本管理** |
| `sleep-evolution` | 😴 **v8.0：SkillOpt-Sleep四阶段(Harvest→Mine→Replay→Consolidate)+夜间离线+跨书籍迁移+降级策略+归档保留+sleep_history索引** |
| `meta-optimizer` | 🎯 **v9.0：四维帕累托(质量×速度×token×留存)+Dream-Rollout探索+SlowUpdate EMA慢更新+元反思五问+跨书迁移三模式+增强版验证门** |
| `skill-compaction` | 📦 **🆕 v10.0：Distill蒸馏+Cross-Benchmark三基准迁移(bench_A_long/bench_B_short/bench_C_commerce)+Compact四类差异化+Rollback-Guard版本回滚+Converge终态收敛(模块数冻结46)+三档部署(full/standard/minimal)+8k token零成本部署** |

## 它和同类有什么不同？

| 维度 | 其他写作Skill | **本工坊 v10.0** |
|:-----|:-------------|:----------------|
| 模块数 | 1-10个 | **46个**，覆盖写作全流程（终态冻结） |
| 技能自进化 | 无 | **SkillOpt 六步循环**+EditOp有界编辑+验证门+学习率预算+拒绝编辑缓冲+best_skill版本管理 |
| 夜间离线自进化 | 无 | **SkillOpt-Sleep 四阶段**(Harvest→Mine→Replay→Consolidate)+跨书籍迁移+降级策略+sleep_history索引 |
| 多目标元优化 | 无 | **四维帕累托**(质量×速度×token×留存)+Dream-Rollout探索+SlowUpdate EMA慢更新+元反思五问+跨书迁移三模式 |
| 自适应技能压缩 | 无 | **Distill 蒸馏**+Cross-Benchmark 三基准迁移+Compact 四类差异化+Rollback-Guard 版本回滚+Converge 终态收敛+三档部署(full/standard/minimal)+8k token 零成本部署 |
| 去AI味 | 简单禁用词替换 | **L1-L4 四层硬门禁**+L3方法论三节+6类逐句审查+段落功能二分法+DeepSeek 734句式+模型感知 |
| 专家审计 | 无 | **五专家面板(E1-E5)**+11维评估+6阶段流程+交叉审计+评分治理红线+预算护栏 |
| 风格配置 | 无 | **8风格维度+7题材路由+8典型档位+风格漂移检测** |
| MBTI 对白 | 无 | **16型对白声线档案+4气质组+群戏冲突设计+情绪表达契合** |
| 温度词库 | 无 | **8类热词+冷词库+微表情库+温度递进原则** |
| 事实快照 | 无 | **16维事实快照+三库协同+5态伏笔状态机+跨会话状态机** |
| 节拍系统 | 无 | **Dramatica 11拍+节拍×伏笔×角色协同矩阵+钩子真假4维+伪因果判定** |
| 模型适配 | 无 | **6大模型**各有专属策略和负面提示 |
| 通感痛觉 | 无 | 900行通感体系（六大原型+四式+剂量管控） |
| 题材覆盖 | 1-3种 | **12+题材**含规则怪谈/无限流/直播等新锐 |
| AI对话修正 | 无 | 6大AI对话通病+各模型修正速查 |
| 读者心理 | 无 | 情绪闭环+代入感+爽点/虐点公式 |
| 人物弧光 | 无 | 正向/负向/关系/多人物弧交织 |
| 连载管理 | 无 | 存稿+断更恢复+读者留存 |
| 描写技法 | 无 | 动作三拍/环境五感/战斗三秒规则 |
| 多线叙事 | 无 | POV切换规范/线索铺设回收体系 |
| 节奏控制 | 无 | 密度曲线/疲劳管理数学模型 |
| 世界体系 | 无 | 力量等级/经济系统/社会阶层 |
| 修改流程 | 无 | 4层结构修改/打乱重排法/8类CT一致性检查 |
| 副线管理 | 无 | 四大副线类型/主副线比例公式 |
| 氛围渲染 | 无 | 五种基础氛围/三叠法/反转构建 |
| 市场战略 | 无 | 平台分析/读者画像/IP评估 |
| 质量门控 | 写完了事 | 写→审→改→检→锁稿5阶段闭环 |
| 架构 | 单文件巨无霸 | **模块化路由**：按需加载，token友好 |

## v6.0+ 三大核心系统

### 1. 五专家审计系统（audit-workflow）

```
                  ┌─────────────────────┐
                  │   Phase 0 专家独立审读   │
                  └──────────┬──────────┘
                             │
        ┌────────┬───────────┼───────────┬────────┐
        ▼        ▼           ▼           ▼        ▼
     ┌─────┐ ┌─────┐    ┌─────┐    ┌─────┐ ┌─────┐
     │ E1  │ │ E2  │    │ E3  │    │ E4  │ │ E5  │
     │语感 │ │剧情 │    │人物 │    │一致 │ │商业 │
     │去AI │ │钩子 │    │对白 │    │性CT │ │留存 │
     └──┬──┘ └──┬──┘    └──┬──┘    └──┬──┘ └──┬──┘
        └────────┴───────────┼───────────┴────────┘
                             ▼
                  ┌─────────────────────┐
                  │  Phase 2 交叉审计 CC1-CC6  │
                  │  标⭐主要矛盾 + 仲裁规则    │
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │  Phase 3 11维加权评分    │
                  │  硬门禁命中→总分上限锁   │
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │  Phase 4 修改方案 A/B/C/D │
                  │  集中兵力打主要矛盾       │
                  └──────────┬──────────┘
                             ▼
                  ┌─────────────────────┐
                  │  Phase 5 自省 meta_review │
                  │  落盘 jsonl + next_focus  │
                  └─────────────────────┘
```

**执行模式**：spawn（并行派生 5 个子 Agent）/ solo（主 Agent 串行扮演 E1-E5）/ code-only（超限降级）

### 2. 三库协同上下文系统（narrative-weaving + state-tracking）

| 库 | 文件 | 职责 |
|:---|:-----|:-----|
| **事实快照库** | `context_bank.json` | 16 维事实状态（角色/道具/地点/时间/能力/关系/伏笔） |
| **伏笔登记库** | `foreshadow_bank.json` | 5 态生命周期（active/recalling/resolved/broken/dropped） |
| **角色档案库** | `characters.json` | MBTI/声线/口头禅/关系网/能力上限 |

**写章前**：读三库 → 生成本章"上下文约束清单"
**写章后**：抽取 16 维快照 → 更新三库 → 触发 E4 一致性检查

### 3. 风格配置系统（style-configuration）

```
写作前定档 → 8 维度配置 → 落盘 style_config.json
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
         写章前读取      写章后对账     10章后允许微调
              │             │             │
              ▼             ▼             ▼
         注入 prompt    漂移检测      drift_threshold
```

**8 维度**：写作风格 / 语气 / 视角 / 时态 / 节奏 / 场景密度 / 对白风格 / 描写密度
**8 档位**：冷峻克制 / 温暖治愈 / 电影感 / 古风文白 / 意识流 / 纪实白描 / 爽文爆爽 / 煽情虐心
**7 题材路由**：玄幻 / 都市 / 科幻 / 历史 / 言情 / 悬疑 / 武侠

## 安全边界

- ❌ 不会自动修改你的细纲/大纲/人设文件
- ❌ 不会在不确认的情况下删除任何内容
- ❌ 不会把小说内容写入公开文件
- ✅ 每次写正文前都会读取最新状态文件
- ✅ 所有关键决策等你确认
- ✅ 评分治理红线 P0：审计计算完成后任何人不得修改分数

## 验证与测试

本仓库含 28 个测试用例（[examples/test-prompts.json](examples/test-prompts.json)），覆盖全部 46 个模块——含 v6.0 审计、v6.1 L1-L4 硬门禁/节拍审计、v6.2 风格配置/MBTI/温度词库/16维快照/评分治理红线、v7.0 SkillOpt 六步循环、v8.0 SkillOpt-Sleep 四阶段、v9.0 多目标帕累托+Dream+EMA、v10.0 技能压缩+蒸馏+跨基准迁移+版本回滚+终态收敛专项用例。

**验收命令——章首连续性检查（core-writing 铁律）：**

```bash
# 检查章首是否误用禁用时间词（第二天/次日/翌日…）
python3 scripts/novel-tools.py --check-continuity your-chapters/
```

**验收命令——字数与AI味分析：**

```bash
# 单章分析（对话占比/AI味密度/段落分布）
python3 scripts/word-count-tool.py chapter-01.md

# 目录批量分析 + 综合评级
python3 scripts/word-count-tool.py chapters/

# JSON 结构化导出（供 CI/流水线集成）
python3 scripts/word-count-tool.py --json chapters/
```

**验收命令——发布就绪度自检（鲁班结构尺）：**

```bash
bash scripts/check-skill-repo.sh
# 期望：PASS: 14 / WARN: 0 / FAIL: 0
```

## 文件结构

```
novel-creation-omnibus/
├── SKILL.md                          # 主路由（任务调度+模块索引+冲突裁决）
├── README.md                         # 安装说明与展示
├── CHANGELOG.md                      # 版本更新记录
├── LICENSE                           # MIT
├── examples/
│   ├── test-prompts.json             # 28个测试用例（含 v6.0-v10.0 专项）
│   ├── demo-output.md                # v6.2 工具链协同输出示例
│   └── sample-chapter.md             # 真实示例章节（约2000字，供工具分析）
├── assets/
│   ├── demo.gif                      # 终端运行录屏（3帧循环）
│   └── demo.tape                     # vhs 录制脚本（可复现）
├── scripts/
│   ├── novel-tools.py                # 章节验证/字数统计/大纲生成/连续性检查
│   ├── word-count-tool.py            # 字数统计与AI味分析（含JSON导出）
│   ├── check-skill-repo.sh           # 发布就绪度自检（鲁班结构尺）
│   ├── gen-demo-gif.py               # 生成 demo.gif 的脚本
│   └── install.sh                    # 一键安装脚本（含验证）
└── references/modules/               # 46个模块，按需加载
    ├── core-writing.md               # 长篇正文写作
    ├── anti-ai-polish.md             # 去AI味 v3.0（L1-L4 四层硬门禁）
    ├── audit-workflow.md             # 审计工作流 v3.0（五专家+评分治理红线）
    ├── plot-engineering.md           # 情节工程 v3.0（Dramatica+钩子真假+伪因果）
    ├── narrative-weaving.md          # 多线叙事 v3.1（三库协同+16维事实快照）
    ├── state-tracking.md             # 状态追踪 v2.0（三库联动+5态伏笔）
    ├── dialogue-mastery.md           # 对话大师 v2.0（MBTI 16型声线档案）
    ├── emotional-climax.md           # 情绪高潮 v2.0（语言温度词库）
    ├── style-configuration.md        # v6.2 风格配置系统
    ├── skill-evolution.md            # v7.0 技能自进化引擎（SkillOpt 集成）
    ├── sleep-evolution.md            # v8.0 离线自进化引擎（SkillOpt-Sleep 集成）
    ├── meta-optimizer.md             # v9.0 多目标元优化器（帕累托+Dream+EMA）
    ├── skill-compaction.md           # 🆕 v10.0 自适应技能压缩（Distill+Compact+Rollback+Converge）
    └── ...                           # 完整列表见 SKILL.md
```

## 版本历史

| 版本 | 亮点 |
|:-----|:------|
| **v10.0** | 📦 🆕 自适应技能压缩与零成本部署：Distill蒸馏提取能力骨架+Cross-Benchmark三基准迁移(bench_A_long/bench_B_short/bench_C_commerce)+Compact四类差异化处理+Rollback-Guard版本回滚三态(accept/accept_with_warning/rollback)+Converge终态收敛三判据(compact/train/pareto)+三档部署(full/standard/minimal)+8k token零成本部署+元能力不可压缩+回滚黑名单+训练降频策略+模块数冻结46（终态宣告） |
| **v9.0** | 🎯 🆕 多目标元优化器：四维帕累托(质量×速度×token×留存)+composite_score加权公式+Dream-Rollout三步探索+SlowUpdate EMA慢更新三档α+正则化项巨变预警+元反思五问(每10epoch)+跨书迁移三模式(直接/抽象/能力)+增强版验证门(四action含pareto_dominated)+transfer_log.jsonl |
| **v8.0** | 😴 🆕 离线自进化引擎：SkillOpt-Sleep 四阶段(Harvest→Mine→Replay→Consolidate)+夜间离线+跨书籍迁移三条件+降级策略四态+Replay三态判定(resolved/persistent/regression)+模式挖掘频次≥3过滤+归档保留策略+sleep_history索引 |
| **v7.0** | 🧬 🆕 技能自进化引擎：SkillOpt 六步循环(Rollout→Reflect→Aggregate→Select→Update→Evaluate)+EditOp有界编辑(ADD/DELETE/REPLACE)+验证门+学习率预算三档衰减+拒绝编辑缓冲三态迁移+best_skill.md版本管理+五维验证分数+训练/验证集70/30隔离 |
| **v6.2** | 🆕 风格配置系统(8维度+7路由) + 评分治理红线P0 + MBTI 16型对白声线 + 语言温度词库 + 16维事实快照schema |
| **v6.1** | 🔧 去AI味L1-L4四层硬门禁+L3方法论三节+6类逐句审查+段落功能二分法；剧情设计钩子真假4维+伪因果+节拍×伏笔×角色协同矩阵；上下文三库协同+5态伏笔状态机+跨会话状态机 |
| **v6.0** | 🆕 审计工作流（五专家面板E1-E5）+ 伏笔库5态状态机 + 16维事实快照 + 8类CT一致性检查 + Dramatica节拍系统 |
| **v5.9.4** | 🔧 自托管体检脚本 + demo.gif录屏 + 真实示例章节 + install.sh验证（check全绿14/0/0） |
| **v5.9.3** | 🔧 鲁班house-style对齐 + marketplace标准格式 + skills.sh徽章 + 验证测试节 |
| **v5.9.2** | 🔧 脚本升级：章首连续性检查 + JSON结构化导出 + 测试用例翻倍(8→16) + 鲁班框架对齐 |
| **v5.9** | 🆕 描写技法 + 多线叙事 + 节奏动力学 + 世界体系 + 修改工作流 + 副线编织法 + 氛围渲染术 + 市场战略 |
| **v5.8** | 🆕 情绪高潮设计(燃/泪/甜/震) + 灵感生成器(8法+30模板) |
| **v5.7** | 🆕 平台规则(起点/飞卢/晋江) + 字数统计工具 |
| **v5.6** | 🆕 场景写作 + 人物弧光 + 长篇连载管理 |
| **v5.5** | 🆕 对话大师 + 开篇钩子 + 情节工程 + 读者心理 |
| **v5.4** | 🆕 模型优化 + 新题材 + 风味写作 + AI味模型感知 |
| **v5.3** | 模块化重构：2540行→模块化，首版发布 |

## 致谢

本项目站在以下项目与方法论的肩膀上，按集成版本依次致谢：

### 📚 框架与方法论

- **鲁班 | Luban 打磨框架** — https://github.com/LearnPrompt/luban-skill
  - 验料 / 访行 / 过尺 / 慢刨 / 回炉 五动作，结构尺 / 实测尺 / 活体尺 三把尺子
  - 本项目的 `scripts/check-skill-repo.sh` 即鲁班结构尺的自托管实现

### 📦 novel-audit-v6.0.0 资产集成（v6.0-v6.2 核心）

> 来自最强小说审计资产包 `novel-audit-v6.0.0`，本项目去AI味/剧情/上下文/审计四大核心系统的母版。

- **去 AI 味系统**（[anti-ai-polish.md](references/modules/anti-ai-polish.md)）
  - L1-L4 四层硬门禁（句式正则 / 人感禁令 / 方法论语义 / 量化指标）
  - DeepSeek 734 句式黑名单 + 51 意象词 + 白名单系统
  - 6 类逐句审查判据 + 段落功能二分法 + 6 大模型感知策略
- **剧情设计系统**（[plot-engineering.md](references/modules/plot-engineering.md)）
  - Dramatica 11 拍节拍结构
  - 钩子真假 4 维判定 + 伪因果 5 大典型
  - 节拍 × 伏笔 × 角色协同矩阵 + 章末钩子 4 型
- **上下文流程系统**（[narrative-weaving.md](references/modules/narrative-weaving.md) + [state-tracking.md](references/modules/state-tracking.md)）
  - 三库协同（context_bank / foreshadow_bank / characters）
  - 16 维事实快照 + 5 态伏笔状态机（active/recalling/resolved/broken/dropped）
  - 跨会话状态机 meta_review_log
- **审计工作流系统**（[audit-workflow.md](references/modules/audit-workflow.md)）
  - 五专家面板 E1-E5（语感 / 剧情 / 人物 / 一致性 / 商业）
  - 11 维评估矩阵 + 6 阶段审计流程 + 交叉审计 CC1-CC6
  - 评分治理红线 P0 四禁令 + 5 档 band + 预算护栏
- **风格配置系统**（[style-configuration.md](references/modules/style-configuration.md)）
  - 8 风格维度 + 7 题材路由 + 8 典型档位 + 风格漂移检测
- **对话与情绪系统**（[dialogue-mastery.md](references/modules/dialogue-mastery.md) + [emotional-climax.md](references/modules/emotional-climax.md)）
  - MBTI 16 型对白声线档案 + 4 气质组对照
  - 语言温度词库（8 类热词 + 冷词库 + 微表情库 + 温度递进原则）

### 🧬 Microsoft SkillOpt v0.2.0 自进化方法论（v7.0-v10.0）

> https://github.com/microsoft/SkillOpt — 把技能文档当作可训练状态，用深度学习的纪律优化它。

- **v7.0 技能自进化引擎**（[skill-evolution.md](references/modules/skill-evolution.md)）
  - 六步训练循环 Rollout→Reflect→Aggregate→Select→Update→Evaluate
  - EditOp 有界编辑（ADD/DELETE/REPLACE）+ 验证门 + 学习率预算 + 拒绝编辑缓冲
- **v8.0 离线自进化引擎**（[sleep-evolution.md](references/modules/sleep-evolution.md)）
  - SkillOpt-Sleep 四阶段 Harvest→Mine→Replay→Consolidate
  - 夜间离线 + 跨书籍迁移 + 降级策略 + 归档保留
- **v9.0 多目标元优化器**（[meta-optimizer.md](references/modules/meta-optimizer.md)）
  - 四维帕累托（质量 × 速度 × token × 留存）+ Dream-Rollout 探索
  - SlowUpdate EMA 慢更新 + 元反思五问 + 跨书迁移三模式
- **v10.0 自适应技能压缩**（[skill-compaction.md](references/modules/skill-compaction.md)）
  - Distill 蒸馏 + Cross-Benchmark 三基准迁移 + Compact 四类差异化
  - Rollback-Guard 版本回滚 + Converge 终态收敛 + 8k token 零成本部署

### 🛠️ 工具与环境

- **Pillow (PIL)** — `assets/demo.gif` 录屏渲染依赖
- **ripgrep** — `scripts/check-skill-repo.sh` 鲁班结构尺底层检索
- 持续迭代于 Hermes Agent 环境

### 🙏 致谢声明

本项目不直接复制上述项目的代码，而是将其方法论与判据内化为 Markdown 模块。所有引用都已标注来源；如原作者认为标注不当或希望调整，欢迎提 issue 沟通。

## License

[MIT](LICENSE)

---

<div align="center">

*写小说，一个工坊就够了。*

</div>
