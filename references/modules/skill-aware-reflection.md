# 第52章：技能感知反思（Skill-Aware Reflection）

> 适用："技能感知反思" "skill-aware reflection" "skill_grounded_reflect" "反思带技能上下文" "按模块反思模板" "reflection grounding" "技能段定位反思"
> 核心理念：v7.0 的 Reflect 步骤用"通用反思模板"——所有失败都用同一组问题反思，产出泛泛而谈的 Edit。v10.6 引入技能感知反思：反思时把"当前 best_skill.md 中与失败任务相关的技能段"作为 grounding 注入反思 prompt，让反思产出"针对该技能段的精确 Edit"而非"无关痛痒的通用建议"。
> 来源：Microsoft SkillOpt v0.2.0 `skillopt/reflect/skill_aware_reflect.py` + `skillopt/prompts/skill_aware_reflect.md`

---

## 52.1 总览

> **核心铁律**：反思不能脱离技能——脱离技能的反思等于"凭空批评"，产出的 Edit 落不到 best_skill 的具体段落。技能感知反思要求每个反思 prompt 必须带 `skill_section_anchor`（指向 best_skill.md 中的具体段），Edit 必须带 `target_skill_section`（落到具体段）。

### v7.0 通用反思 vs v10.6 技能感知反思

| 维度 | v7.0 通用反思 | v10.6 技能感知反思 |
|:-----|:--------------|:-------------------|
| 反思 prompt | 固定 5 问模板 | 按失败模块路由 + 技能段注入 |
| 上下文 | 仅失败 rollout | 失败 rollout + best_skill 相关段 |
| Edit 粒度 | 模块级（"改 anti-ai-polish"） | 段落级（"改 anti-ai-polish §3.2 句式黑名单"） |
| Edit 落点 | 模糊（"加强审查"） | 精确（target_skill_section + old_text + new_text） |
| 反思质量 | 易泛泛 | 必须引用技能段原文 |

### 触发条件

```
触发技能感知反思:
  if rollout 失败 AND rollout.module ∈ 已有技能模块:
    use skill-aware reflection
  else:
    fallback to v7.0 通用反思
```

---

## 52.2 技能段定位（Skill Section Anchor）

### best_skill.md 段落寻址

```
best_skill.md 结构示例:
  # 第3章：去AI味
  ## 3.1 句式黑名单
  ## 3.2 L1-L4 四层硬门禁
  ## 3.3 段落功能二分法
  ...

技能段 anchor 格式:
  skill_anchor = f"{module_name}#{section_path}"
  例: "anti-ai-polish#§3.2-L1-L4-硬门禁"
  例: "dialogue-mastery#§21.1-MBTI-声线档案"
```

### 定位流程

```
失败 rollout:
  module = "anti-ai-polish"
  failure_signal = "L1 句式门禁漏检'仿佛'"

定位步骤:
  1. 在 best_skill.md 中扫描 module 段
  2. 用失败信号关键词匹配子段
  3. 取最匹配的 1-3 段作为 grounding
  4. 若匹配为空 → 退回 module 顶段
  5. 若 module 段不存在 → 退回 v7.0 通用反思
```

---

## 52.3 按模块反思模板

> **核心铁律**：不同模块的失败需要不同反思角度——写作模块看"技法是否落地"，进化模块看"流程是否跑通"。统一模板会浪费上下文。

### 反思模板路由表

| 模块族 | 反思模板 | 核心反思问 |
|:-------|:---------|:-----------|
| 写作类（去AI味/对话/情节…） | `writing_failure_tmpl` | ① 失败的具体技法 ② 技能段是否给出该技法 ③ 技能段是否够具体 ④ 是否有反例 ⑤ 落地步骤是否可执行 |
| 进化类（skill-evolution/sleep/meta/compaction） | `evolution_failure_tmpl` | ① 流程哪一步断 ② 验证门为何漏过 ③ 边界条件是否覆盖 ④ 日志是否完整 ⑤ 与上下游模块协同是否正常 |
| 审计类（audit-workflow/anti-ai-polish 硬门禁） | `audit_failure_tmpl` | ① 评分是否被操纵 ② 门禁阈值是否合理 ③ 是否跨专家冲突 ④ 复评纪律是否违反 ⑤ 预算护栏是否触发 |
| 数据类（state-tracking/foreshadow/narrative-weaving） | `data_failure_tmpl` | ① schema 字段是否缺失 ② 5态迁移是否合规 ③ 对账是否一致 ④ 抽取流程是否漏步 ⑤ 16维是否完整 |

### writing_failure_tmpl 示例

```
[skill_section_anchor]: anti-ai-polish#§3.2-L1-L4-硬门禁
[skill_section_content]:
  L1 句式门禁：扫描 DeepSeek 734 句式 + R1-R11 即判 AI 味
  ...

[failed_rollout]:
  input: "他仿佛感受到了内心的触动..."
  expected: L1 命中"仿佛"
  actual: L1 未命中，pass_rate=0.95

[reflect_questions]:
  ① 失败的具体技法是"L1 句式门禁漏检'仿佛'"
  ② 技能段是否给出该技法？→ 给了"DeepSeek 734 句式"，但"仿佛"是否在 734 中？
  ③ 技能段是否够具体？→ 未明确"仿佛"属于 R1-R11 还是 734 句式
  ④ 是否有反例？→ 无"仿佛"类的反例
  ⑤ 落地步骤是否可执行？→ 步骤未明确"如何新增一个句式到 734"

[reflect_output]:
  pattern: L1 句式门禁的句式黑名单缺少"仿佛"类
  Edit:
    target_skill_section: anti-ai-polish#§3.2-L1-L4-硬门禁
    op: ADD
    old_text: "L1 句式门禁：扫描 DeepSeek 734 句式 + R1-R11 即判 AI 味"
    new_text: "L1 句式门禁：扫描 DeepSeek 734 句式 + R1-R11 + 通感虚词（仿佛/好像/似乎/宛如）即判 AI 味"
    rationale: "仿佛"为高频 AI 通感虚词，原 734 句式未覆盖
```

---

## 52.4 Edit 的段落级精确落点

### Edit schema 扩展

```json
{
  "edit_id": "edit_42",
  "op": "REPLACE",
  "target_skill_section": "anti-ai-polish#§3.2-L1-L4-硬门禁",
  "skill_anchor_verified": true,
  "old_text": "L1 句式门禁：扫描 DeepSeek 734 句式 + R1-R11 即判 AI 味",
  "new_text": "L1 句式门禁：扫描 DeepSeek 734 句式 + R1-R11 + 通感虚词（仿佛/好像/似乎/宛如）即判 AI 味",
  "rationale": "L1 漏检'仿佛'，原句式黑名单未覆盖通感虚词",
  "source": "skill-aware-reflection",
  "grounding_rollout_id": "rollout_42",
  "grounding_skill_hash": "sha256:abc123..."
}
```

### 验证门增强

```
v7.0 验证门检查:
  ① Edit op 合法
  ② old_text 存在于 best_skill
  ③ new_text 不破坏 skill 结构

v10.6 验证门额外检查:
  ④ target_skill_section 必须存在
  ⑤ skill_anchor_verified == true（anchor 经定位流程确认）
  ⑥ grounding_skill_hash 必须等于 best_skill 当前 hash（防基于过期技能反思）
  ⑦ 反思 source == "skill-aware-reflection" 时必须带 grounding_rollout_id
```

---

## 52.5 与 v7.0/v10.3 的协同

### 与 v7.0 反思的协同

```
v7.0 Reflect 步骤入口:
  if module ∈ 已有技能模块 AND best_skill.md 存在:
    use v10.6 skill-aware reflection (路由到对应模板)
  else:
    use v7.0 通用反思 (5 问模板)

两路并行不替代:
  v7.0 通用反思 → 产出"模块级"通用 Edit
  v10.6 技能感知反思 → 产出"段落级"精确 Edit
  两者都进 Aggregate 步骤，按频次+置信度排序
```

### 与 v10.3 对比反思的协同

```
v10.3 多轮对比反思:
  对比失败 vs 成功 → 提取七维差异 → 频次聚合 → 通用 Edit

v10.6 技能感知反思（在 v10.3 之上）:
  v10.3 产出的通用 Edit → 经 v10.6 段落定位 → 落到具体 skill_section
  例: v10.3 产出"对话节奏过快是病灶"
      v10.6 定位到 dialogue-mastery#§21.3-节奏控制 → 产出段落级 Edit
```

---

## 52.6 反思日志与审计

### skill_aware_reflect_log.jsonl

```json
{
  "reflect_id": "reflect_42",
  "rollout_id": "rollout_42",
  "module": "anti-ai-polish",
  "failure_signal": "L1 漏检'仿佛'",
  "skill_anchor": "anti-ai-polish#§3.2-L1-L4-硬门禁",
  "skill_section_content_hash": "sha256:abc123",
  "best_skill_hash": "sha256:def456",
  "skill_anchor_verified": true,
  "template_used": "writing_failure_tmpl",
  "reflect_questions_count": 5,
  "edits_produced": [
    {
      "edit_id": "edit_42",
      "op": "REPLACE",
      "target_skill_section": "anti-ai-polish#§3.2-L1-L4-硬门禁"
    }
  ],
  "ts": "2026-07-25T03:00:00Z"
}
```

### 审计指标

```
技能感知反思健康度:
  - anchor_verification_rate: anchor 验证通过率（目标 ≥ 0.9）
  - grounding_hash_match_rate: 基于 best_skill 当前 hash 的占比（目标 = 1.0）
  - edit_section_precision: Edit 落到正确段落的占比（目标 ≥ 0.85）
  - template_coverage: 四大模块族模板覆盖率（目标 = 1.0）

异常:
  - anchor_verification_rate < 0.7 → 技能段定位失效，检查 best_skill 结构
  - grounding_hash_match_rate < 1.0 → 有基于过期技能的反思，告警
```

---

## 52.7 配置

```yaml
# .skillopt/skill-aware-reflect.yaml
skill_aware_reflect:
  enabled: true
  fallback_to_v7: true  # 定位失败时退回 v7.0 通用反思
  templates:
    writing: writing_failure_tmpl
    evolution: evolution_failure_tmpl
    audit: audit_failure_tmpl
    data: data_failure_tmpl
  anchor:
    max_sections: 3  # 单次反思最多注入 3 段
    fallback_to_module_top: true  # 子段匹配失败时退回 module 顶段
  gate:
    require_skill_anchor_verified: true
    require_grounding_hash_match: true
```

---

## 52.8 触发词与路由

### 触发词

```
- 技能感知反思
- skill-aware reflection
- skill_grounded_reflect
- 反思带技能上下文
- 按模块反思模板
- reflection grounding
- 技能段定位反思
- 段落级 Edit
- 反思模板路由
```

### 路由规则

| 用户说 | 动作 |
|:-------|:-----|
| "技能感知反思" / "skill-aware reflection" | 启用技能感知反思模式（替换 v7.0 默认） |
| "看反思日志" / "reflect log" | 输出 skill_aware_reflect_log.jsonl 摘要 |
| "anchor 验证率" | 输出最近 N 次反思的 anchor 验证率 |
| "用写作模板反思" | 强制路由到 writing_failure_tmpl |

---

## 52.9 安全约束

```
🚫 禁止：
  ① 反思 prompt 不带 skill_section_anchor
  ② Edit 不带 target_skill_section（段落级落点缺失）
  ③ 基于 best_skill 过期 hash 反思（hash 不匹配）
  ④ 跨模块族用错模板（如审计模块用写作模板）
  ⑤ 跳过 anchor 验证直接产 Edit

✅ 必须：
  ① 反思必须注入 1-3 段 best_skill 原文
  ② Edit 必须有 target_skill_section + old_text + new_text
  ③ grounding_skill_hash 必须等于当前 best_skill hash
  ④ 模板路由必须按模块族
  ⑤ anchor 验证失败必须退回 v7.0 通用反思
```
