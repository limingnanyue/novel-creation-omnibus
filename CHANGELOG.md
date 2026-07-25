# Changelog

## [v8.0.0] — 2026-07-25
### SkillOpt-Sleep Integration — 离线自进化引擎集成（新增第 44 个模块）

> 集成 Microsoft SkillOpt v0.2.0 `skillopt-sleep` CLI 方法论：夜间离线复盘过去会话，挖掘反复出现的失败模式，重放代表性任务，在验证门后巩固已验证的技能编辑——不打扰日间写作。

### Added · 新增第 44 个模块：sleep-evolution.md（离线自进化引擎）
- **Sleep 四阶段流水线**（来源：SkillOpt-Sleep `skillopt-sleep` CLI）
  - ① Harvest（会话收割）→ ② Mine（模式挖掘）→ ③ Replay（任务重放）→ ④ Consolidate（技能巩固）
  - 完整契约表：每阶段输入/输出/必做动作/禁忌
- **Harvest 会话收割**
  - 6 类输入源（章节输出/审计报告/meta_review_log/rejected_edits/读者反馈/风格档案）
  - sessions.jsonl schema（session_id/ts/chapter/score/band/failures/audit_path）
  - 时间窗口默认 7 天（可配置 1-30 天）
  - 会话数 < 10 自动降级
- **Mine 模式挖掘**
  - 三步流程（失败聚类→频次过滤→根因归并）
  - patterns.json schema（pattern_id/frequency/root_cause/representative_session/suggested_edit/confidence）
  - 频次阈值 min_support=3（偶发错误不触发 Replay）
  - 模式挖掘审计清单（频次/根因/代表性/置信度/互斥）
- **Replay 任务重放**
  - 用当前 best_skill 重跑代表性失败任务
  - Replay 三态判定（resolved/persistent/regression）
  - replay_results.json schema（pattern_id/original_failure/new_outcome/new_score/score_delta/raw_patch）
- **Consolidate 技能巩固**
  - 复用 v7.0 六步循环的 Aggregate→Select→Update→Evaluate→Gate
  - sleep_log.jsonl 落盘（sleep_id/window_days/sessions_harvested/patterns_mined/gate_action/score_delta）
  - 与 v7.0 日间训练的协同时序（日间训练→夜间 Sleep→次日读最新 best_skill）
- **跨书籍 Sleep（高级模式）**
  - 跨书籍迁移三条件（题材相近/失败模式通用/验证集严格提升）
  - 迁移失败时 Edit 进书籍 A 专属缓冲，不影响书籍 B
- **Sleep 调度与触发**
  - 三种触发（定时凌晨02:00/手动/阈值缓冲池>50）
  - 前置检查五项（日间训练未结束/会话数/ best_skill存在/磁盘/验证集一致）
  - 降级策略四态（会话不足/磁盘不足/验证集污染/日间训练中）
- **归档保留策略**
  - sleep_<date>/ 目录归档（sessions/patterns/replay_results/consolidate_patch/gate_result/sleep_log_entry）
  - sleep_history.jsonl 历史索引
  - 最近30次完整保留，30-90次仅摘要，90次以上删除
  - accept 产物永不删除（best_skill 溯源）

### Changed
- SKILL.md：版本 7.0→8.0，模块数 43→44，新增 sleep-evolution 路由+索引+文件结构，新增 8 个触发词
- README.md：标题/徽章/模块数 43→44，新增 Sleep 徽章，对比表新增"夜间离线自进化"行，版本历史新增 v8.0
- marketplace.json：版本 7.0.0→8.0.0，description 同步
- test-prompts.json：新增 test-26 Sleep 四阶段用例（总数 26）
- 鲁班结构尺自检：14 PASS / 0 WARN / 0 FAIL（全绿）

---

## [v7.0.0] — 2026-07-25
### SkillOpt Integration — 技能自进化引擎集成（新增第 43 个模块）

> 集成 Microsoft SkillOpt v0.2.0（https://github.com/microsoft/SkillOpt）方法论：把技能文档当作冻结 agent 的可训练状态，用深度学习的纪律优化它——epoch/batch/learning-rate/validation-gate，但不碰模型权重。

### Added · 新增第 43 个模块：skill-evolution.md（技能自进化引擎）
- **SkillOpt 六步训练循环**（来源：SkillOpt v0.2.0 engine 模块）
  - ① Rollout → ② Reflect → ③ Aggregate → ④ Select → ⑤ Update → ⑥ Evaluate
  - 完整契约表：每阶段输入/输出/必做动作/禁忌
- **EditOp 有界编辑三操作**（来源：SkillOpt `Edit` / `EditOp` 类型）
  - ADD / DELETE / REPLACE 三种原子操作，不得整文件重写
  - Edit 完整 schema：op/content/target/support_count/source_type/merge_level/update_origin/update_target
  - 有界编辑五条纪律（target 可定位/ADD 先读原文/DELETE 查交叉引用/REPLACE 保功能位/数量受学习率约束）
- **验证门 Validation Gate**（来源：SkillOpt `GateResult` / `GateAction`）
  - GateResult schema：action(accept/reject/tie)/current_skill/current_score/best_skill/best_score/best_step
  - 判定规则：新分数 > 旧分数 + min_delta(0.05) 才 accept
  - held-out 验证集 70/30 隔离
  - 五维验证分数 D1语感/D2钩子/D3人物/D4一致性/D5商业（精简版，单章<30秒）
- **学习率预算三档衰减**（来源：SkillOpt textual learning rate）
  - 快档 0.3（epoch 1-3 大改）/ 中档 0.15（epoch 4-6 微调）/ 慢档 0.05（epoch 7+ 精修）
  - 学习率只能衰减不能回升
  - 预算超支按 support_count 降序截断
- **拒绝编辑缓冲三态迁移**（来源：SkillOpt rejected-edit buffer）
  - buffered → retried → promoted/permanent_drop
  - 连续 3 轮被拒或未被 Select 选中即永久移除
  - 缓冲池审计清单（大小膨胀/反复重试/放弃原因/互斥 Edit）
- **best_skill.md 版本管理**
  - 始终保留 best_skill.md 作为部署产物
  - epoch 级目录归档（skill_before/after + patch + gate_result + rollout_results）
  - best_skill.meta.json：version/best_score/parent_version/rollback_path
- **与现有模块联动**
  - Reflect 阶段调用 audit-workflow 五专家
  - Rollout 阶段调用 anti-ai-polish L1-L4（D1）
  - Reflect 调用 plot-engineering 节拍审计（D2）/ dialogue-mastery MBTI（D3）
  - Evaluate 调用 narrative-weaving 16维快照（D4）/ style-configuration 漂移检测（D5）
  - state-tracking 负责跨 epoch 状态保存

### Changed
- SKILL.md：版本 6.2→7.0，模块数 42→43，新增 skill-evolution 路由+索引+文件结构，新增 9 个触发词
- README.md：标题/徽章/模块数 42→43，新增 SkillOpt 徽章，对比表新增"技能自进化"行，版本历史新增 v7.0
- marketplace.json：版本 6.2.0→7.0.0，description 同步
- 鲁班结构尺自检：14 PASS / 0 WARN / 0 FAIL（全绿）

---

## [Unreleased] — 2026-07-25
### Examples Refresh — 实例更新（v6.2 工具链演示补完 + 去AI味示例重写）

### Changed · 示例章节去AI味重写
- `examples/sample-chapter.md`: 替换示例章节
  - 旧：《刚被裁，全人类进了数据副本》（陈默/林晚，被裁程序员）
    - AI 味问题：L2 "像"字比喻 ×3（"像念一道判决书"/"像在说今天天气不好"/"这话听着像安慰"）
    - AI 意象："暖黄色的光落在她脸上"
    - 章末 AI 味："也许真的不一样了"
    - 解说腔："可安慰在这个时候一点用都没有"
  - 新：《夜班最后一单》（老周/女乘客，夜班出租车司机拉到去殡仪馆的女孩）
    - 过 L1-L4 四层硬门禁：零 em-dash、零"像"字比喻、零 AI 意象
    - 真人门检命中：自嘲（"你有病啊大半夜的"）、具体细节（零三年刀疤/八年/小卖部）、口吻（"几点了都"）
    - 章末钩子：信息悬念型（照片背面字）+ "天快亮了"
    - 字数 775，对话占比 26.5%，AI 味密度 1.29 处/千字（低）
- `examples/demo-output.md`: 全部工具链数据同步切换为"夜班最后一单"
  - 风格档案：电影感档 → 纪实白描档（genre=悬疑）
  - MBTI 声线：ISTJ/ENFJ → ISTP（老周）/ INFJ（女乘客）/ ESFJ（老婆）
  - 温度词：0→0→-1→+2→+1 递进
  - 五专家审计：总分 8.78（Band A），CC2 照片伏笔待回收
  - 16 维快照：3 条伏笔（main 照片/mid 来世/short 零三年那人）
  - Dramatica 节拍：B1日常+B2触发+B3初拒+B5假象胜利
- `README.md`: 效果示例节选同步切换为"夜班最后一单"
- `assets/demo.gif`: 重新生成（3 帧，47 KB，采集新章节真实工具输出）

### Added · 测试用例扩展
- `examples/test-prompts.json`: 新增 8 个测试用例（test-17 ~ test-24），总数 16 → 24
  - test-17 v6.0 审计工作流·五专家会诊（audit-workflow）
  - test-18 v6.1 去AI味·L1-L4 四层硬门禁（anti-ai-polish）
  - test-19 v6.1 情节工程·Dramatica 11 拍节拍审计（plot-engineering）
  - test-20 v6.2 风格配置·定档与漂移检测（style-configuration）
  - test-21 v6.2 对话大师·MBTI 16 型声线（dialogue-mastery）
  - test-22 v6.2 情绪高潮·语言温度词库（emotional-climax）
  - test-23 v6.2 多线叙事·16 维事实快照抽取（narrative-weaving）
  - test-24 v6.2 审计·评分治理红线 P0（audit-workflow）

### Changed
- README.md：测试用例数 16 → 24，文件结构注释同步更新
- 鲁班结构尺自检：14 PASS / 0 WARN / 0 FAIL（全绿）

---

## [v6.2.0] — 2026-07-25
### Asset Completion — 深度资产补完（5 大资产集成）

> 基于 novel-audit-v6.0.0.zip 中尚未集成的核心资产进行补完：风格配置系统、MBTI 16 型、温度词库、评分治理红线、16 维事实快照 schema。

### Added · 新增第 42 个模块：style-configuration.md（风格配置系统）
- **8 风格维度**（来源：style_dimensions.json v1.4）
  - 写作风格 / 语气 / 视角 / 时态 / 节奏 / 场景密度 / 对白风格 / 描写密度
  - 每维度含完整选项列表和默认值
- **8 典型档位**（维度组合速查）
  - 冷峻克制档 / 温暖治愈档 / 电影感档 / 古风文白档 / 意识流档 / 纪实白描档 / 爽文爆爽档 / 煽情虐心档
- **7 题材路由**（来源：intent_router.json v1.4）
  - 玄幻/都市/科幻/历史/言情/悬疑/武侠 7 大题材触发关键词
  - 题材 × 风格档推荐映射
  - 题材 × 11 维评估器权重调整矩阵
- **风格档案 schema**（style_config.json）
  - 8 维度配置 + lock_until_chapter + allow_drift_after + drift_threshold
- **风格漂移检测**
  - 写章前读取 + 写章后对账 + 漂移维度数 > threshold 告警
  - 风格漂移 5 大典型（语气/视角/节奏/对白/描写）
- **风格档案变更纪律**
  - 前 10 章锁定 / 10-30 章微调 / 30 章后允许调整但必须落盘
- **跨模块联动**：7 个模块与 style_config 联动

### Enhanced · audit-workflow.md v2.0 → v3.0（审计工作流深度补强）
- **新增评分治理红线 P0**（来源：score_governance.json）
  - 4 条禁令：禁止覆写 / 禁止主观调分 / 禁止评级操纵 / 禁止 LLM 覆盖确定性结果
  - 5 档评分 band：A(90-100) / B(80-89) / C(70-79) / D(60-69)🔒freeze / F(0-59)🔒freeze
  - 复评纪律：最大 3 轮 / 解冻门 / 禁止表面修补（F 级须触及根因维度）
  - 禁止字段：manual_override / adjusted_by / human_score
  - 硬门禁与总评联动：AI 句式≥1 锁 3.0 / CT 矛盾≥1 锁 2.5 / 事实硬伤≥1 锁 2.0
- **新增预算护栏**（来源：audit_budget.json）
  - 单章最大子 Agent 派生数 6 / token 软上限 60000 / 超限降级 code-only
  - 自动降级链细化版（spawn → solo → code-only → 仅 E1+E4）
- **新增专家 findings 完整输出 schema**（来源：expert_output_schema.md v5.6.1）
  - 13 字段完整定义（含 module_summary / cross_cut_notes / sentence_review）
  - severity 标尺 S1-S4 与代码层对齐
  - 逐句审查契约（6 类必审 + 7 条纪律）
- **新增 E3 / E5 完整角色卡**
  - E3 人物与对白专家：5 大核心判断 + 3 个交叉区职责 + 硬约束
  - E5 商业化与整体专家：4 大核心判断 + 2 个交叉区职责 + 仲裁优先级最高
  - 5 专家主审维度速查表（完整版）

### Enhanced · dialogue-mastery.md v1.0 → v2.0（集成 MBTI 16 型对白声线档案）
- **来源**：mbti_16_full.json v1.4
- **16 型对白声线速查表**：每型含对白节奏/词汇偏好/反应模式/典型口头禅
- **4 气质组对照**：SJ 传统派 / SP 现实派 / NF 理想派 / NT 理性派
- **对白声线判定流程**（E3 专家必经 4 步）
- **MBTI 跨角色群戏冲突设计**：4 对典型冲突组合
- **MBTI 与情绪表达契合**：4 气质组 × 4 情绪（愤怒/悲伤/喜悦/恐惧）对照表
  - 解决 AI 把所有角色情绪表达标准化的问题

### Enhanced · emotional-climax.md v1.0 → v2.0（集成语言温度词库）
- **来源**：temperature_words.json v4.0.0
- **8 类热词情绪档案**：愤怒(+3) / 喜悦(+3) / 紧张(+2) / 轻蔑(+1) / 平静(0) / 尴尬(0) / 恐惧(-2) / 悲伤(-1)
  - 每类含典型词 + 微表情库
- **冷词库**：客观描述(-1) / 抽象总结(-2) / 万能动词(-2)
- **温度词在 4 类高潮中的应用**：燃/泪/甜/震 各自的温度区间和微表情密度
- **5 条使用纪律**：禁止堆叠 / 温度递进 / 微表情锚定 / 冷热对比 / MBTI 契合
- **温度词审计清单**（E1/E3 共审 7 项）

### Enhanced · narrative-weaving.md v3.0 → v3.1（集成 16 维事实快照完整 schema）
- **来源**：snapshot_schema_15d.json v1.4（实际 16 维）
- **16 维字段定义**：characters_known/mentioned/present + items_held/lost/gained + locations_reached/left/described + time_markers/time_of_day + abilities_revealed/used + relationships_state + foreshadow_planted/recalled
- **完整 JSONL 格式示例**
- **16 维 × 8 类 CT 一致性检查对照**（E4 专家用此对账）
- **事实快照抽取流程**（5 步必经）
- **5 个硬指标预警**：角色过载/道具过多/场景过频/能力膨胀/关系变化过快

### Changed
- SKILL.md：版本升级到 v6.2，模块数 41 → 42
  - description 新增 v6.2 强化说明
  - 新增触发词 18 个（风格配置/写作风格/定调/题材路由/风格维度/风格统一/声口统一/风格漂移/定档风格/风格档/风格配置文件/统一调性/风格一致性/MBTI/声线档案/温度词/微表情/情绪温度/评分治理/预算护栏）
  - 路由表新增风格配置行
  - 模块索引新增 style-configuration 条目
  - 文件结构新增 style-configuration.md
- 各模块版本号升级：dialogue-mastery v1.0→v2.0 / emotional-climax v1.0→v2.0 / narrative-weaving v3.0→v3.1 / audit-workflow v2.0→v3.0

### 资产来源
- novel-audit-v6.0.0.zip 中尚未集成的核心文件：
  - config/style_dimensions.json（8 风格维度）
  - config/intent_router.json（7 题材路由）
  - config/mbti_16_full.json（16 型完整档案）
  - config/temperature_words.json（语言温度词库）
  - config/score_governance.json（评分治理红线）
  - config/audit_budget.json（预算护栏）
  - config/snapshot_schema_15d.json（16 维事实快照 schema）
  - experts/E3_character.md（人物与对白专家完整角色卡）
  - experts/E5_commercial.md（商业化与整体专家完整角色卡）
  - experts/expert_output_schema.md（专家 findings 完整输出 schema）

---

## [v6.1.0] — 2026-07-25
### Deep Optimization — 着重强化去AI味/剧情设计/上下文流程

> 基于用户提供的 novel-audit-v6.0.0.zip 完整资产（含 experts/E1-E5、panel.md、meta_critic.md、cross_cut_matrix.md、ai_flavor_patterns.json、ai_flavor_whitelist.json 等核心文件）进行深度优化升级。

### Enhanced · anti-ai-polish.md v2.0 → v3.0（去AI味重点强化）
- **新增 L1-L4 四层硬门禁体系**（D1 维度安全底线）
  - L1 句式正则层：DeepSeek 734 句式 + R1-R11 + Gate + qu-ai-wei 51 条
  - L2 人感禁令层：em-dash / "像"字 / 文言腔 / 拟人 / 网文黑名单
  - L3 方法论语义层：真人门检 / 过度消毒 / AI 不敢写
  - L4 量化指标层：困惑度 / TTR / 可读性 / 句长方差
  - 硬约束：命中即扣分，不可被专家上调绕过
- **新增 L3 方法论三节硬门禁**（最关键的"人味"判据）
  - 一、真人门检判据：6 类真人强信号（自纠/方言/自嘲/具体细节/口吻/访谈实录）
  - 二、过度消毒反制判据：3 类必须保留的毛边（个人化/具体感受/圈层表达）
  - 三、AI 不敢写测试判据：5 类"AI 不敢写"信号（自嘲/不确定/冒犯/降格/私人细节）
- **新增 6 类逐句审查判据**（E1 必经，覆盖全文每句）
  - 文言文表达 / 电报式简略句式 / 比喻排比密度 / 解说腔 / 节奏断点 / AI 套话残留
  - **电报式 6 变体图谱**（脚本抓不到的漏检）：
    A 省略主语连环 / B 虚词清零 / C 名词孤岛 / D 对话电报 / E 心理电报 / F 动作电报
  - 每变体含判据+抓例+放行例+放行场景
- **新增段落功能二分法**（解说腔/电报体的真正判据）
  - 解说腔 vs 人感的 4 维对照（段落功能/判别口诀/典型样貌/节奏特征）
  - 判别口诀："找不到一个正在经历此刻的角色身体" = 解说腔
- **新增逐句审查输出格式**（sentence_review schema）
  - reviewer / review_time / total / passed / failed / pass_rate / failures
  - pass_rate < 0.85 触发深度复审

### Enhanced · plot-engineering.md v2.0 → v3.0（剧情设计重点强化）
- **新增钩子真假 4 维判定**（E2 专家必判）
  - 信息悬念 / 情感悬念 / 危机悬念 / 反转悬念
  - 每类含真钩子特征 vs 假悬念特征对照
  - 假悬念 5 种典型病灶（答案太明显/威胁不真实/角色没人气/反转无伏笔/章末空钩）
- **新增伪因果判定**（CC3 交叉区核心）
  - 真因果 vs 伪因果 4 维对照（推动力/后果承担/可预测性/替代可能性）
  - 伪因果 5 大典型（机械降神/巧合堆叠/反派降智/金手指越权/剧情需要式行为）
  - 4 类修复方向
- **新增节拍 × 伏笔 × 角色协同矩阵**
  - 节拍 × 伏笔投放/回收矩阵（11 拍 × 4 类伏笔的投放/回收时机）
  - 节拍 × 戏剧角色 7 型就位表（11 拍 × 7 角色的就位状态）
  - 节拍审计三维交叉检查清单
- **新增章末钩子设计 4 型**
  - 信息悬念型 / 危机悬念型 / 反转悬念型 / 情感悬念型
  - 章末钩子 5 大失败模式（空钩/假钩/慢钩/断钩/重复钩）
  - 章末钩子与下一章章首的衔接规则

### Enhanced · narrative-weaving.md v2.0 → v3.0（上下文流程重点强化）
- **新增三库协同·上下文恢复流程**
  - 三库职责划分（context_bank / foreshadow_bank / characters）
  - 写章前的三库查询流程（4 步必经流程）
  - 写章后的三库更新流程（4 步必经流程）
- **新增 5 态伏笔状态机详细迁移规则**
  - 完整状态机图（active/recalling/resolved/broken/dropped）
  - 5 条迁移规则细化（触发条件 + 检测方）
  - 伏笔审计 5 个硬指标预警
- **新增跨会话状态机·meta_review_log**
  - 状态文件位置（.novel_state/<book-id>/meta_review_log.jsonl）
  - 完整 JSONL schema（misjudgments/omissions/principal_contradiction_check/next_focus）
  - 下次审计时的注入流程
  - 自省纪律（fix_action 必须可执行）

### Enhanced · audit-workflow.md v1.0 → v2.0（审计工作流强化）
- **新增 spawn / solo 双路径执行**
  - 双路径对照（spawn 并行 vs solo 串行）
  - solo 串行纪律（每轮只戴一顶帽子）
  - 自动降级链（spawn → solo → code-only）
- **新增 11 维评估器与专家完整映射**
  - 11 维 × 5 专家完整映射表（含主审/协同/硬指标软指标标注）
  - 第一梯队（0.10 权重，6 项硬核维度）
  - 第二梯队（0.08 权重，5 项软指标）
  - 评分规则（硬门禁命中 → 总分上限锁 3.0）
- **新增 Phase 0-5 详细操作清单**
  - 每阶段的输入/禁忌/输出/必做动作
  - 4 类修改方案对照（A 精准手术 / B 稳健提升 / C 风格重塑 / D 结构重构）
- **新增 finding 完整 schema**
  - 11 字段完整定义（含 cross_cut / code_supplement / llm_vs_code / exempt 等）

### Enhanced · state-tracking.md v1.0 → v2.0（状态追踪强化）
- **新增三库联动**（与 narrative-weaving §9 深度集成）
  - 写章前查询三库流程
  - 写章后更新三库流程
- **新增 5 态伏笔状态机检查清单**
  - 5 状态追踪动作
  - 5 个硬指标预警
- **新增跨会话状态机·meta_review_log 集成**

### Changed
- SKILL.md：版本升级到 v6.1
  - description 新增 v6.1 强化说明
  - 新增触发词：逐句审查/电报体/解说腔/段落功能二分法/伪因果/机械降神/节拍/Dramatica/伏笔状态机/三库协同/跨会话状态
- 各模块版本号统一升级（v2.0 → v3.0 / v1.0 → v2.0）
- 关联模块交叉引用更新

### 资产来源
- novel-audit-v6.0.0.zip（449MB，含 experts/ 全套 + kb/ 知识库 + config/ 配置）
- 重点提取文件：
  - experts/E1_tone.md（18KB，L1-L4 四层硬门禁 + 6 类逐句审查判据 + 段落功能二分法 + L3 方法论三节）
  - experts/E2_plot.md（钩子真假判定 + 伪因果判定 + CC3 交叉区）
  - experts/E4_consistency.md（事实一致性优先级 + 6+1 道门禁）
  - experts/cross_cut_matrix.md（6 个交叉区 + 4 条仲裁规则）
  - experts/panel.md（spawn/solo 双路径 + Phase 0-4 编排契约）
  - experts/meta_critic.md（E0 自省官 + meta_review_log.jsonl）
  - config/dramatica_beats.json（11 拍 + 7 戏剧角色）
  - config/foreshadow_bank.json（5 态状态机）
  - config/renovel_consistency.json（8 类 CT 检查）
  - config/llm_evaluator_11d.json（11 维评估器）
  - config/ai_flavor_patterns.json（qu-ai-wei 51 条 + Humanizer-zh 24 模式）
  - config/ai_flavor_whitelist.json（5 类白名单）

---

## [v6.0.0] — 2026-07-22
### Major Integration — novel-audit-v6.0.0 资产集成

### Added
- **新增模块 `audit-workflow.md`**（第41个模块）：五专家面板(E1-E5)、
  11维评估矩阵、6阶段审计流程、CC1-CC6交叉审计、跨会话状态机
  (meta_review_log.jsonl)、降级链。来源 novel-audit-v6.0.0 专家面板架构。

### Enhanced（4个现有模块升级到 v2.0）
- **anti-ai-polish.md v2.0**：集成 DeepSeek 句式黑名单系统
  - 734条句式模板（A级564），优先级MAX
  - 51个高频意象词（cat22，整词命中即报警）
  - 小说创作高频A级句式（cat6：开篇/人物/对话/动作/心理/情感/冲突/转折/结尾）
  - 情感/环境/外貌A级句式（cat14-17）
  - 特定场景A级句式（cat21：修仙/悬疑/商战/宫廷/末世）
  - 白名单系统（5类圈内术语豁免，避免误杀）
  - min_hits阈值表（避免单词误杀）
  - AI味打分公式（A级×3 + A-级×2 + 意象词×1.5）
- **plot-engineering.md v2.0**：集成 Dramatica 11拍节拍结构
  - 全书11拍序列（B1日常→B11新世界，含位置百分比区间）
  - 节拍审计要点（结构完整性检查 + 节奏错位诊断）
  - 戏剧角色7型（主角/对手/理性/情感/守护者/欺骗者/陪衬）
  - 爽点密度与反差判定（E2专家语义判断）
- **narrative-weaving.md v2.0**：集成伏笔库系统 + 事实快照
  - 伏笔库5态状态机（active/recalling/resolved/broken/dropped）
  - type与max_gap映射（main=60/mid=30/short=10/gag=3章）
  - 伏笔字段定义（id/type/trigger_keywords/recall_keywords/max_gap/status）
  - 16维事实快照（characters/items/locations/time/abilities/relationships/foreshadow）
  - 钩子真假判定（真钩子vs假悬念四类对照）
- **revision-workflow.md v2.0**：集成一致性检查 + 交叉审计
  - 8类CT一致性检查（CT1时间/CT2地点/CT3道具/CT4信息越界/CT5性格/CT6设定/CT7数量/CT8称谓）
  - 6个交叉区（CC1-CC6：对白×人设/伏笔×回收/人物×剧情/世界观×设定/钩子×留存/节奏呼吸感）
  - 4条仲裁规则（去重/冲突消解优先级/互补合并/无法调和标注conflict_pending）

### Changed
- SKILL.md：版本升级到 v6.0，模块数 40→41，新增审计触发词
  （审计/审稿/体检/诊断/专家会诊/多视角审查/质量评估）
- 模块索引新增 audit-workflow 条目
- 文件结构新增 audit-workflow.md

### 资产来源
- novel-audit-v6.0.0（用户提供的 zip 包）
- 提取文件：deepseek_ai_sentence_blacklist.json / ai_flavor_patterns.json /
  ai_flavor_whitelist.json / dramatica_beats.json / foreshadow_bank.json /
  renovel_consistency.json / cross_cut_matrix.md / panel.md / meta_critic.md /
  llm_evaluator_11d.json / snapshot_schema_15d.json

## [v5.9.4] — 2026-07-22
### Self-Contained Tooling & Full Birth-Checklist Pass

### Added
- `scripts/check-skill-repo.sh`: 自托管鲁班结构尺检查脚本(源自
  LearnPrompt/luban-skill),项目可独立体检,不依赖外部 luban 路径。
  运行 `bash scripts/check-skill-repo.sh .` 即可发布前自检。
- `scripts/gen-demo-gif.py`: 用 PIL 渲染终端输出生成 demo.gif,展示
  novel-tools 与 word-count-tool 的真实运行结果(3帧循环)。
- `examples/sample-chapter.md`: 真实示例章节(约2000字,含对话/叙述/场景),
  供 word-count-tool 和 check-continuity 演示真实分析能力。
- `assets/demo.gif`: 真实录屏产物(47KB,3帧),清除最后一个 WARN。

### Changed
- `scripts/install.sh`: 增加安装前 Node.js 版本检查(v18+)、安装失败提示、
  安装后 novel-tools.py 可运行性验证、装完第一句话指引。
- README 效果示例节: 产物前置——demo.gif 嵌入展示位置。
- check-skill-repo 结果: 12 PASS/1 WARN → **14 PASS/0 WARN/0 FAIL**(全绿)。

## [v5.9.3] — 2026-07-22
### Luban Framework Alignment — House-Style & Marketplace

### Added
- `assets/demo.tape`: 可复现的 vhs 录制脚本，展示 novel-tools.py 和
  word-count-tool.py 的真实终端输出，填补 check-skill-repo 的 demo WARN
- README 新增「验证与测试」节：含章首连续性检查、字数与AI味分析、JSON
  导出三条验收命令，符合 luban house-style 的"可验证产物"要求
- README 新增「文件结构」节（luban house-style 标准节）
- README 新增 skills.sh 安装计数徽章（luban 出生证必备件）
- README 新增锚点导航（luban house-style 铁律：首屏10秒讲清价值）
- README 首屏新增引语钩子（luban house-style 铁律：钩子是引语不是功能清单）
- README 产物前置：效果示例节移至安装命令之前（luban house-style 铁律）

### Changed
- `.claude-plugin/marketplace.json`: 升级为 luban plugin marketplace 标准格式
  （owner/metadata/plugins[]/version/author/source/category/homepage），
  原 schema_version+skills[] 格式已弃用
- README 对比表：删除"全行业独一份"大词（luban 铁律：不写大词），
  改为具体描述"900行通感体系（六大原型+四式+剂量管控）"
- README 版本历史表新增 v5.9.2 和 v5.9.3 条目
- README 致谢节后新增 License 节（luban house-style 标准节）
- README 装完第一句话改为可复制的 text 代码块（luban 出生证：装完第一句话）

## [v5.9.2] — 2026-07-22
### Feature Upgrades — Tooling & Test Coverage

### Added
- `scripts/novel-tools.py --check-continuity`: new command that enforces the
  core-writing.md rule "章首禁用任何时间词". Scans chapter openings (skipping
  titles/headings) and flags 15 forbidden time words + 5 filler words, with
  context snippets. Supports single-file and directory batch mode.
- `scripts/word-count-tool.py --json`: structured JSON export for all three
  modes (file / directory / compare). Directory mode includes an aggregate
  `summary` block (files, total chars, avg dialog ratio, avg AI smell,
  estimated read time). Enables pipeline/CI integration.
- `examples/test-prompts.json`: 8 new test cases (test-09 ~ test-16) covering
  all v5.9 modules — descriptive-craft, narrative-weaving, pacing-dynamics,
  world-systems, revision-workflow, subplot-craft, atmosphere-mood,
  market-strategy. Total now 16 cases (was 8).

### Changed
- `scripts/novel-tools.py` docstring updated with new command usage
- `scripts/word-count-tool.py` docstring updated with `--json` usage

## [v5.9.1] — 2026-07-22
### Maintenance & Consistency Fixes

### Fixed
- marketplace.json: updated stale description (said 25 tools/19 modules, now correctly 40 modules v5.9)
- CHANGELOG.md: corrected inconsistent module counts in v5.4-v5.8 entries
  (trajectory now consistent: 19→22→26→29→30→32→40)
- SKILL.md: removed duplicate `反转` trigger (appeared at both line 56 and 107)
- examples/demo-output.md: fixed stray English word `highway` in Chinese text
- scripts/word-count-tool.py: fixed broken rglob pattern `*.[mdt][dx]*t`
  (replaced with proper `*.md` + `*.txt` set union)
- scripts/word-count-tool.py: replaced bare `except:` with specific exceptions
- scripts/word-count-tool.py: `--compare` mode now displays units (% / 处)
  instead of computing and discarding them
- scripts/word-count-tool.py: `--watch` mode now produces an actual directory
  snapshot with timestamp instead of only printing usage text
- scripts/novel-tools.py: added FileNotFoundError/UnicodeDecodeError handling
- scripts/novel-tools.py: `--count` now excludes whitespace (consistent with
  word-count-tool.py) and reports CJK char count
- scripts/novel-tools.py: `--validate` now also reports paragraph count
- scripts/novel-tools.py: `--outline` now generates a usable template
  (volume table + per-chapter detail skeleton) instead of an empty table
- LICENSE: added missing copyright holder

### Changed
- SKILL.md `last_updated` bumped to 2026-07-22

## [v5.9] — 2026-06-16
### Major Expansion — 8 New Modules (32→40)

### Added
#### 🆕 描写技法 `descriptive-craft.md`
- 动作描写三拍式节奏（起势→执行→结果）
- 环境五感矩阵（视觉/听觉/嗅觉/触觉/味觉）+ 环境即情绪映射表
- 外貌描写三原则（不堆砌/有功能/留白）+ 特征记忆点设计
- 战斗/冲突场面分类写法（武术/枪战/群战）+ 三秒钟规则
- 细节具象化公式（形容词→具体动作/感官/比喻）+ 三连法
- 战斗后"身体账本"（体力/受伤/心理/装备损耗）

#### 🆕 多线叙事 `narrative-weaving.md`
- POV三大视角对比（第一人称/第三人称有限/全知）
- POV切换规则（黄金法则：同一场景只用一个POV）
- 三种主流叙事结构（平行式/汇流式/回溯式）
- 时间锚定与闪回三条铁律
- 线索四种类别（章节级/卷级/全书级/系列级）
- 线索密度公式（每10章=2-3新投+1回收）
- 线索铺设技巧（轻描淡写/重复强调/反常识/信息差）

#### 🆕 节奏动力学 `pacing-dynamics.md`
- 三种基础节奏（快/中/慢）+ 各平台建议字数
- 四级密度标准与公式（极高→低）
- 读者疲劳曲线+四级重置策略（微/小/中/大重置）
- 信息释放"喂食"策略（七成原则）
- 长短章交替模式（A/B/C三种模式）
- 各题材节奏模板（宠文/悬疑/爽文）

#### 🆕 世界运转体系 `world-systems.md`
- 力量等级设计三原则+跨级战斗合理范围
- 经济系统（货币/资源层级+物价锚定+叙事功能）
- 政治格局最小模型（三方势力动态平衡）
- 六种势力变化模式（结盟/背叛/兼并/渗透/平衡/崩塌）
- 组织类型模板（宗门/家族/商会/军队/学院）
- 社会阶层流动设计（向上/向下/平行/伪装）
- 编年史锚点事件+冰山原则

#### 🆕 修改工作流 `revision-workflow.md`
- 四层修改体系（结构→章节→句子→校对）
- 结构修改"打乱重排"法
- 章节修改"五问法"
- 逐句精修"七刀"（去AI味用词过滤）
- 句子节奏调整（短/中/长句交替）
- 读者反馈分级处理（逻辑bug→个人口味）

#### 🆕 副线编织法 `subplot-craft.md`
- 四大副线类型（浪漫/成长/阴谋/日常）
- 各题材主副线建议比例表
- 副线密度公式+生命周期（引入→成长→高潮→收束）
- 收束规则（每卷至少收1条）
- 多人物支线轮换策略+出场退场节奏

#### 🆕 氛围渲染术 `atmosphere-mood.md`
- 五种基础氛围构建（压抑/紧张/温暖/诡异/悲伤）
- 氛围构建三阶段（引入→加深→释放）
- "三叠法"层层递进
- 氛围反转手法（最大冲击）
- 氛围滤网（POV角色情绪匹配）
- 悬念四层递进+暴风雨前的宁静+留白技巧

#### 🆕 市场战略 `market-strategy.md`
- 网文平台格局分析（起点/番茄/飞卢/晋江/书旗）
- 2025年题材热度矩阵（10+题材热度/竞争/新人友好度）
- 读者消费行为四层分层（轻度→核心）
- 差异化定位三问+竞争分析框架
- 平台选择策略（按写作优势/签约后运营节奏）
- IP改编潜力判断+短剧化特征

### Changed
- SKILL.md → v5.9: 40 modules (was 32), 8 new routing entries, 30+ new trigger words
- README → v5.9: 40 modules, new feature descriptions, updated comparison table (v5.9), new badges
- Description updated to v5.9 with all 8 new modules documented
- Conflict resolution table: added 3 new entries for descriptive-craft, narrative-weaving, atmosphere-mood interactions
- File structure updated with all 8 new module paths
- Version bumped to 5.9

## [v5.8] — 2026-06-16

### Added
- Emotional Climax module: 4 climax types (fiery/tearful/sweet/shocking),
  formula-driven 7-step structures for each type, genre-climax matching table,
  long-novel climax placement strategy (30-chapter distribution), post-climax buffer design
- Idea Generator module: 8 idea generation methods (cross-domain/role reversal/
  extreme hypothetical/rule-breaking/time-shift/perspective shift/scale push/
  rule extrapolation), character formula, 30 plot templates, worldbuilding formula,
  idea evaluation checklist, idea warehouse management system
- 12+ new trigger words: 高潮, 燃, 催泪, 甜, 震惊, 灵感, 脑洞, 卡文, etc.

### Changed
- SKILL.md → v5.8: 32 modules (was 30), +2 routing entries, updated module index
- Description updated to v5.8 with emotional-climax and idea-generator
- Version bumped to 5.8

## [v5.7] — 2026-06-16

### Added
- Platform Rules module: 起点/飞卢/晋江 writing rules covering reader demographics,
  genre preferences, first 3 chapters, contract standards, writing style, 
  cross-platform adaptation guide, platform selection decision tree
- Word count tool (scripts/word-count-tool.py): per-chapter stats, batch directory 
  analysis, dialog-to-narrative ratio, AI-smell keyword density, chapter length 
  distribution, estimated reading time, chapter comparison, writing quality grading

### Changed
- SKILL.md → v5.7: 30 modules (was 29), +platform-rules routing
- README → v5.7: added platform rules section
- Version bumped to 5.7

## [v5.6] — 2026-06-16

### Added
- Scene Crafting module: 4-scene elements, 6 scene types (action/dialogue/emotional/
  suspense/transition/reveal), scene entry/exit techniques, scene bridging,
  internal scene rhythm, scene writing AI-smell checklist
- Character Arcing module: 3 arc types (positive/negative/flat), 7-stage positive arc,
  5-stage negative arc, relationship arcs, multi-character arc weaving,
  arc consistency checklist
- Serial Management module: draft strategy, update cadence management, rolling outline,
  reader retention tactics (new + old readers), recovery after hiatus, outline adjustment
  during serialization, serialization AI-smell checklist
- 18+ new trigger words for scene, character arc, and serial management

### Changed
- SKILL.md → v5.6: 29 modules (was 26), 3 new routing entries, updated module index
- Version bumped to 5.6

## [v5.5] — 2026-06-16

### Added
- Dialogue Mastery module: 8 dialogue functions, 4-speed pacing, 3-level subtext,
  5-voice dimensions, action interleaving, group conversation management,
  AI dialogue detection & correction, scene-specific (arguments, confessions, farewells)
- Opening Hooks module: 12 blockbuster opening patterns, 300-word survival checklist,
  5 chapter-bridge techniques, 4 cliffhanger types, full Chapter 1 audit checklist
- Plot Engineering module: Super-short loop (Tomato) / scroll (Qidian) structures,
  4 density tiers, 7 reversal types, foreshadowing management, 6-level conflict escalation,
  tension-relaxation rhythm curve
- Reader Psychology module: Emotional closure mechanism, 3-factor immersion,
  gratification psychology, angst formulas, TOP10 dropout causes, reader mood dashboard,
  genre-specific psychological profiles
- 20+ new trigger words for dialogue, hooks, plot, and reader psychology
- All 4 modules are model-aware and genre-aware

### Changed
- SKILL.md → v5.5: 26 modules (was 22), 12 new routing entries, updated index table
- Version bumped to 5.5

## [v5.4] — 2026-06-16

### Added
- Model optimization module: 6 models (Claude/DeepSeek/GPT/Qwen/Kimi/豆包) with
  individual diagnostic tables, negative prompts, and genre-match matrix
- New genres module: 规则怪谈, 无限流, 直播文, 末世废土, 悬疑推理, 种田日常, 跨题材融合
- Flavorful writing module: 5-sense detection, colloquial speech 6 techniques,
  micro-mannerism system, environmental interaction, food writing, specificity engine
- Model-aware anti-AI polish: per-model detection triggers, correction tables,
  and 15-second quick fix cheat sheet

### Changed
- SKILL.md → v5.4: 22 modules (was 19), updated routing table with 10 new entries
- anti-ai-polish.md: added 8.6 model-aware section
- Version bumped to 5.4

## [v5.3] — 2026-06-16

### Added
- Full modular refactor: 2540-line all-in-one → 19 modular files + SKILL.md
- Human-touch README with narrative opening
- MIT LICENSE, 8 test cases
- scripts/, assets/, examples/ directories
- AI-quantification scoring (12 indicators × 0-10 scale)
- "必杀留人" / six anti-AI barriers system

### Changed
- Hybrid dual distribution (modular + all-in-one)
- SKILL.md streamlined 2540→199 lines
- Model-level negative instruction for anti-AI taint

### Fixed
- Structure validation: 9/9 PASS (previously 3 FAILs)

## [v5.2] — Initial release
- All-in-one single file, basic novel workflow
