# Changelog

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
