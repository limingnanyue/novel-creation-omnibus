# Changelog

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
