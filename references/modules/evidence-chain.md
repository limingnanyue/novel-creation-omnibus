# 第47章：证据链与提示模板注册表（Evidence Chain & Prompt Registry）

> 适用："证据链" "evidence chain" "evidence.jsonl" "决策重建" "提示模板注册" "prompt registry" "user overrides" "用户覆盖" "每晚证据" "sleep evidence" "审计重建"
> 核心理念：v8.0 Sleep 离线进化产出 best_skill.md，但每夜的决策过程（harvest 了什么 / mine 出什么模式 / replay 哪些任务 / reflection 提了什么 Edit / gate 判了什么）是黑盒。v10.1 引入 evidence.jsonl 链——把每夜的完整决策链落盘，可重建、可审计、可回放。同时引入 live prompt-template registry，让用户覆盖默认提示词。
> 来源：Microsoft SkillOpt v0.2.0 Unreleased `evidence.jsonl` chains + live prompt-template registry

---

## 47.1 解冻宣告

> v10.0 宣告"模块数冻结=46，下次升级需触发解冻流程"。v10.1 触发解冻——经元反思五问确认：现有 46 模块无法覆盖"决策可重建性"与"提示词可定制性"两项新能力，故解冻模块数，进入第二阶段进化。

### 解冻五问（元反思）

| # | 问题 | v10.0 答案 | v10.1 答案 | 解冻触发 |
|:---|:-----|:-----------|:-----------|:---------|
| ① | 现有模块能否覆盖"决策重建"？ | 否（Sleep 只产 best_skill，不产决策链） | 是（evidence.jsonl） | ✓ |
| ② | 现有模块能否覆盖"提示词覆盖"？ | 否（提示词硬编码在模块里） | 是（prompt-registry） | ✓ |
| ③ | 解冻后是否打破帕累托前沿？ | — | 否（只增不减） | ✓ |
| ④ | 解冻后训练健康度是否下降？ | — | 否（evidence 辅助训练） | ✓ |
| ⑤ | 是否经过 Dream-Rollout 验证？ | — | 是（dream 集验证通过） | ✓ |

五问全中 → 解冻，模块数从 46 → 47。

---

## 47.2 Evidence Chain 总览

> **核心铁律**：每夜 Sleep 必须产出 evidence.jsonl 链，记录从 harvest 到 gate 的每个决策。无 evidence 的 Sleep 视为"黑盒 Sleep"，不得更新 best_skill。

### 五阶段证据链

```
┌─────────────────────────────────────────────────────────────┐
│                每夜 Evidence Chain（evidence.jsonl）          │
└─────────────────────────────────────────────────────────────┘

  ① Harvest Evidence    ② Mine Evidence    ③ Replay Evidence
  ─────────────────     ──────────────     ────────────────
  收割了哪些会话          挖掘出哪些模式      重放了哪些任务
  sessions.jsonl         patterns.jsonl     replays.jsonl
       │                      │                   │
       ▼                      ▼                   ▼
  ④ Reflection Evidence    ⑤ Gate Evidence
  ──────────────────────    ──────────────
  反思提了哪些 Edit          验证门判了什么
  raw_patches.jsonl         gate_results.jsonl
       │                          │
       └────────────┬─────────────┘
                    ▼
            evidence.jsonl（合并链）
            落盘到 .skillopt/sleep/{date}/evidence.jsonl
```

### Evidence Record Schema

```json
{
  "evidence_id": "ev-2026-07-25-001",
  "date": "2026-07-25",
  "stage": "harvest",
  "ts": "2026-07-25T02:00:00Z",
  "input": {
    "session_sources": ["chapters/", "audit_reports/", "meta_review_log.jsonl"],
    "session_count": 23
  },
  "output": {
    "harvested_sessions": 18,
    "filtered_out": 5,
    "filter_reasons": ["sub-agent transcript", "plugin-generated"]
  },
  "decision": "harvest 18 of 23 sessions",
  "rationale": "排除 sub-agent 与 plugin 会话，避免污染模式挖掘",
  "hash": "sha256:abc123..."
}
```

---

## 47.3 五阶段证据契约

| # | 阶段 | evidence 字段 | 必记录内容 | 落盘文件 |
|:---|:-----|:--------------|:-----------|:---------|
| ① | Harvest | `harvest_ev` | 会话源/总数/过滤数/过滤原因 | `harvest.jsonl` |
| ② | Mine | `mine_ev` | 模式 ID/频次/LLM 置信度/是否进 Replay | `mine.jsonl` |
| ③ | Replay | `replay_ev` | 任务 ID/重放分数/三态判定 | `replay.jsonl` |
| ④ | Reflection | `reflect_ev` | RawPatch ID/EditOp 类型/目标模块/support_count | `reflect.jsonl` |
| ⑤ | Gate | `gate_ev` | GateResult/action/四维分数/帕累托判定 | `gate.jsonl` |

### 证据链完整性铁律

```
🚫 禁止：
  ① 跳过任一阶段的 evidence 记录
  ② 事后修改 evidence（只追加，不修改）
  ③ 删除超过 30 天的 evidence（归档保留）

✅ 必须：
  ① 每条 evidence 含 hash（前后链验证）
  ② 每夜产出 evidence_summary.md（人类可读）
  ③ evidence 可用于重建决策（replay_evidence 命令）
```

---

## 47.4 Prompt Template Registry

> **核心铁律**：模块里的提示词不再硬编码——所有提示词进 registry，用户可覆盖，覆盖记录可审计。

### Registry Schema

```yaml
# .skillopt/prompt-registry.yaml
prompts:
  - id: analyst_error
    module: skill-evolution
    default: |
      你是错误分析师。分析以下失败样本，提取病灶，建议 Edit。
      失败样本：{failure}
    user_override: null
    override_ts: null
    override_by: null

  - id: harvest_filter
    module: sleep-evolution
    default: |
      过滤 sub-agent 与 plugin 会话，保留核心写作会话。
    user_override: |
      额外过滤：字数<500 的会话也排除。
    override_ts: "2026-07-25T10:00:00Z"
    override_by: "user@local"

  - id: gate_judge
    module: meta-optimizer
    default: |
      比对新旧分数，判定 accept/reject/tie/pareto_dominated。
    user_override: null
```

### 覆盖三态

| 状态 | 含义 | 加载优先级 |
|:-----|:-----|:----------|
| `default` | 模块内置默认 | 最低 |
| `user_override` | 用户覆盖 | 最高 |
| `pinned` | 锁定不可覆盖 | 高于 default，低于 user_override |

### 覆盖审计

```
每次覆盖必须记录：
  - override_ts：覆盖时间
  - override_by：覆盖者（user/system）
  - override_reason：覆盖原因
  - previous_override：上一版覆盖内容（可回滚）

落盘到 .skillopt/prompt-overrides.jsonl
```

---

## 47.5 决策重建（Replay Evidence）

> **核心铁律**：evidence.jsonl 不仅用于审计，还可用于重建——从 evidence 重跑某夜的决策，验证 Sleep 是否正确执行。

### 重建命令

```bash
# 重建某夜的完整决策链
skillopt-sleep replay-evidence --date 2026-07-25

# 仅重建某一阶段
skillopt-sleep replay-evidence --date 2026-07-25 --stage mine

# 对比重建结果与原结果
skillopt-sleep replay-evidence --date 2026-07-25 --diff
```

### 重建三步

```
Step 1: 加载 evidence.jsonl
  读取 .skillopt/sleep/2026-07-25/evidence.jsonl
  验证 hash 链完整性

Step 2: 重跑决策
  用 evidence 中的 input 重跑该阶段
  记录新 output

Step 3: 对比
  新 output vs 原 output
  一致 → 标 "reproducible"
  不一致 → 标 "diverged"，进 divergence_log
```

### 重建契约

| 重建结果 | 含义 | 动作 |
|:---------|:-----|:-----|
| `reproducible` | 新旧一致 | Sleep 可信 |
| `diverged` | 新旧不一致 | 进 divergence_log，触发调查 |
| `incomplete` | evidence 缺失 | 标"黑盒 Sleep"，不更新 best_skill |

---

## 47.6 与 v8.0/v9.0/v10.0 的协同

### 与 v8.0 Sleep 的协同

```
v8.0 Sleep 四阶段 → 每阶段产出 evidence
       │
       ▼
v10.1 Evidence Chain → 合并为 evidence.jsonl
       │
       ▼
次日可用 replay-evidence 重建决策
```

### 与 v9.0 Meta-Optimizer 的协同

```
v9.0 元反思五问（每 10 epoch）→ 读 evidence.jsonl
       │
       ▼
基于 evidence 判断训练健康度
（而非只看分数曲线）
```

### 与 v10.0 Compaction 的协同

```
v10.0 Compact 产出 best_skill_min.md
       │
       ▼
v10.1 Evidence Chain 记录 Compact 决策
（哪些模块被压缩/哪些被保留/为什么）
       │
       ▼
compact_evidence.jsonl 可用于重建压缩决策
```

---

## 47.7 触发词与路由

### 触发词

```
- 证据链
- evidence chain
- evidence.jsonl
- 决策重建
- 提示模板注册
- prompt registry
- user overrides
- 用户覆盖
- 每晚证据
- sleep evidence
- 审计重建
- replay evidence
- 解冻
- unfreeze
```

### 路由规则

| 用户说 | 动作 |
|:-------|:-----|
| "查看证据链" / "evidence chain" | 输出最近一夜的 evidence_summary.md |
| "重建决策" / "replay evidence" | 跑 replay-evidence 命令 |
| "覆盖提示词" / "prompt override" | 编辑 prompt-registry.yaml |
| "查看提示词注册表" / "prompt registry" | 输出当前 registry 状态 |
| "解冻" / "unfreeze" | 触发解冻五问，确认后解冻模块数 |

---

## 47.8 安全约束

```
🚫 禁止：
  ① 删除或修改已落盘的 evidence（只追加）
  ② 跳过任一阶段的 evidence 记录
  ③ 删除超过 30 天的 evidence（归档保留）
  ④ 覆盖 pinned 提示词
  ⑤ 无 override_reason 的覆盖

✅ 必须：
  ① 每条 evidence 含 hash 链
  ② 每夜产出人类可读 summary
  ③ 覆盖记录可回滚
  ④ 重建结果落盘 divergence_log
```
