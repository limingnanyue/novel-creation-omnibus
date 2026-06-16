# Changelog

## [v5.7] — 2026-06-16

### Added
- Platform Rules module: 起点/飞卢/晋江 writing rules covering reader demographics,
  genre preferences, first 3 chapters, contract standards, writing style, 
  cross-platform adaptation guide, platform selection decision tree
- Word count tool (scripts/word-count-tool.py): per-chapter stats, batch directory 
  analysis, dialog-to-narrative ratio, AI-smell keyword density, chapter length 
  distribution, estimated reading time, chapter comparison, writing quality grading

### Changed
- SKILL.md → v5.7: 40 modules (was 39), +platform-rules routing
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
- SKILL.md → v5.6: 39 modules (was 36), 3 new routing entries, updated module index
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
- SKILL.md → v5.5: 36 modules (was 32), 12 new routing entries, updated index table
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
- SKILL.md → v5.4: 28 tool modules (was 25), updated routing table with 10 new entries
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
