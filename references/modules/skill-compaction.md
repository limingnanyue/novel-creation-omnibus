# 第46章：自适应技能压缩与零成本部署（Skill-Compaction）

> 适用："技能压缩" "skill compaction" "best_skill 压缩" "蒸馏" "distill" "跨基准迁移" "cross benchmark" "版本回滚" "rollback skill" "零成本部署" "minimal skill" "蒸馏版" "compact skill" "技能瘦身" "知识沉淀"
> 核心理念：v7.0 让技能可训练，v8.0 让技能夜间进化，v9.0 让技能多目标优化。v10.0 解决最后一步——把经过 N 轮训练后膨胀的 `best_skill.md` 压缩回可零成本部署的 minimal 版本，同时不丢核心能力。**压缩即收敛，收敛即终态。**
> 来源：Microsoft SkillOpt v0.2.0 `distill` / `compact` / `cross-benchmark-transfer` 实验控制

---

## 46.1 Skill-Compaction 总览

> **核心铁律**：技能每经过一个 epoch 的训练，token 量都会增长（ADD 多于 DELETE）。10 个 epoch 后 best_skill.md 可能从 30k token 膨胀到 80k token。v10.0 的使命是把这种膨胀"压回去"——产出 `best_skill_min.md`（≤40% 原体积），且在 held-out 验证集上分数损失 ≤ 5%。

### 压缩三目标

| 目标 | 符号 | 单位 | 阈值 | 说明 |
|:-----|:-----|:-----|:-----|:-----|
| 体积压缩率 | C_ratio | 0-1 | ≤ 0.40 | min_token / best_token |
| 能力保留率 | C_keep | 0-1 | ≥ 0.95 | min_score / best_score |
| 部署零成本 | C_zero | bool | true | min_token ≤ context_budget（默认 8k token） |

### 压缩契约

```
┌─────────────────────────────────────────────────────────────┐
│                Skill-Compaction 流水线（终态收敛）            │
└─────────────────────────────────────────────────────────────┘

  best_skill.md（膨胀态）
        │
        ▼
  ① Distill              ② Cross-Benchmark       ③ Compact
  ─────────              ──────────────          ────────
  提取核心能力骨架         多基准迁移验证           瘦身产出 min 版
  按权重排序删冗余         ≥3 个基准都通过         best_skill_min.md
        │                       │                       │
        ▼                       ▼                       ▼
  CapabilityMap         BenchmarkResult        CompactResult
                                                      │
                                                      ▼
                                          ④ Rollback-Guard
                                          ────────────────
                                          版本回滚兜底
                                          分数损失>5% 自动回滚
                                                      │
                                                      ▼
                                          ⑤ Converge
                                          ──────────
                                          收敛判定
                                          模块数冻结=46
```

### 五阶段契约表

| # | 阶段 | 输入 | 输出 | 必做动作 | 禁忌 |
|:---|:-----|:-----|:-----|:---------|:-----|
| ① | **Distill** | best_skill.md + 训练历史 | `CapabilityMap` | 提取每个模块的核心能力骨架（≤3 行）+ 调用频次排序 | 不得删除 support_count ≥ 5 的能力 |
| ② | **Cross-Benchmark** | CapabilityMap + 3 基准集 | `BenchmarkResult` | 在 3 个独立基准（不同题材/不同模型）上验证 | 不得只在单一题材上验证 |
| ③ | **Compact** | CapabilityMap + BenchmarkResult | `best_skill_min.md` | 按权重截断 + 合并同源 + 删冗余示例 | 不得删除安全边界/总纲铁律 |
| ④ | **Rollback-Guard** | best_skill_min.md + 验证集 | `GuardResult` | 比对 min vs best 分数，损失>5% 自动回滚 | 不得跳过回滚判定 |
| ⑤ | **Converge** | GuardResult + 训练日志 | `ConvergeResult` | 收敛判定（连续 3 次压缩无提升=收敛） | 收敛后冻结模块数 |

---

## 46.2 Distill 蒸馏：提取能力骨架

> **核心铁律**：蒸馏不是删除——是把每个模块里"反复被验证有用"的能力提取成骨架，把"一次性示例"和"长篇论证"压缩成单行引用。骨架保留意图，丢弃冗余解释。

### CapabilityMap Schema

```json
{
  "skill_version": "v9.0",
  "modules": [
    {
      "module": "anti-ai-polish",
      "token_count": 8500,
      "call_count": 47,
      "success_rate": 0.92,
      "core_capabilities": [
        {
          "cap_id": "CAP-001",
          "intent": "L1-L4 四层硬门禁",
          "skeleton": "L1 句式正则 → L2 人感禁令 → L3 方法论语义 → L4 量化指标",
          "support_count": 38,
          "keep": true
        },
        {
          "cap_id": "CAP-002",
          "intent": "DeepSeek 734 句式黑名单",
          "skeleton": "734 条正则+示例对照表",
          "support_count": 12,
          "keep": true
        },
        {
          "cap_id": "CAP-003",
          "intent": "示例段落对比",
          "skeleton": "（冗余示例，压缩为引用 §2.5）",
          "support_count": 2,
          "keep": false
        }
      ],
      "distilled_token_count": 3200,
      "compression_ratio": 0.38
    }
  ]
}
```

### Distill 三步

```
Step 1: 提取核心能力
  对每个模块：
    - 扫描训练历史，统计每条规则/示例的 support_count
    - support_count ≥ 5 → 标 keep=true（核心能力）
    - support_count < 5 → 标 keep=false（候选删除）
    - 提取每条 keep=true 能力的 ≤3 行骨架

Step 2: 排序与权重
  按 (support_count × success_rate) 降序排列
  高权重能力优先保留完整骨架
  低权重能力压缩为单行引用

Step 3: 产出 CapabilityMap
  落盘到 .skillopt/distill/capability_map_v{N}.json
  记录每模块的 compression_ratio 预估值
```

### Distill 三纪律

```
🚫 不得删除：
  ① 总纲铁律（6条）
  ② 安全边界（5条）
  ③ 任务路由表（核心调度，删了就崩）
  ④ 跨规则冲突裁决表（决策依据）

✅ 可以压缩：
  ① 冗余示例（同一规则下超过 3 个示例的，留 1 删其余）
  ② 长篇论证（把"为什么这样做"压缩成"做什么"）
  ③ 重复定义（多模块共有的概念，只留首次定义）
  ④ 过时规则（被后续 epoch 替换的旧规则）
```

---

## 46.3 Cross-Benchmark Transfer：跨基准迁移验证

> **核心铁律**：压缩后的 min 版必须在 ≥3 个独立基准上验证通过才能部署。单一基准上的好成绩 = 过拟合该基准，不是真压缩。

### 三基准集设计

| 基准集 | 题材 | 模型 | 用途 |
|:-------|:-----|:-----|:-----|
| `bench_A_long` | 长篇网文（玄幻/都市） | Claude 3.5 | 主力场景验证 |
| `bench_B_short` | 短篇虐文/规则怪谈 | DeepSeek V3 | 跨题材泛化 |
| `bench_C_commerce` | 番茄爆文/系统流 | Qwen 2.5 | 跨模型泛化 |

### Cross-Benchmark 三步

```
Step 1: 在三基准上分别跑 best_skill_min.md
  每个基准取 10 个 held-out 章节
  记录四维分数（Q/S/T/R）

Step 2: 计算迁移得分
  transfer_score = min(bench_A_Q, bench_B_Q, bench_C_Q) / best_skill_Q
  transfer_score ≥ 0.95 → 通过
  transfer_score < 0.95 → 该能力标"不可压缩"，回 Distill 重做

Step 3: 产出 BenchmarkResult
  落盘到 .skillopt/distill/benchmark_v{N}.json
  记录每模块在三基准上的分数矩阵
```

### 三基准迁移矩阵

```
                  bench_A_long   bench_B_short   bench_C_commerce
                  ────────────   ─────────────   ────────────────
anti-ai-polish        0.97            0.96             0.94     ← 边界，保留完整
plot-engineering      0.98            0.97             0.95
dialogue-mastery      0.96            0.99             0.93     ← 商业向弱，保留完整
core-writing          0.99            0.97             0.96
audit-workflow        0.95            0.95             0.95
skill-evolution       0.94            0.94             0.94     ← 元能力，不压缩
sleep-evolution       0.94            0.94             0.94     ← 元能力，不压缩
meta-optimizer        0.93            0.93             0.93     ← 元能力，不压缩

🚨 任一基准分数 < 0.90 → 该模块不进 Compact 阶段，保留 best 版
```

---

## 46.4 Compact 瘦身：产出 best_skill_min.md

> **核心铁律**：Compact 不是机械删字——是按 CapabilityMap 的 keep 标记 + Benchmark 的迁移分数，产出"四类内容差异化处理"的 min 版。

### 四类内容处理策略

| 内容类型 | 处理策略 | 体积变化 | 例子 |
|:---------|:---------|:---------|:-----|
| **核心骨架**（keep=true + 高迁移） | 保留完整 | 不变 | L1-L4 四层门禁定义 |
| **次要能力**（keep=true + 中迁移） | 压缩为骨架+1示例 | -60% | DeepSeek 734 句式 → 保留规则+10 条样例 |
| **冗余示例**（keep=false） | 压缩为引用 | -90% | "见 references/modules/xxx.md §N" |
| **元能力**（skill/sleep/meta） | 不压缩 | 不变 | v7/v8/v9 三个模块原样保留 |

### Compact 算法

```
def compact(skill_md, capability_map, benchmark_result):
    output = []
    for section in skill_md.sections:
        cap = capability_map.find(section.module)
        bench = benchmark_result.find(section.module)

        if cap.is_meta_capability:  # skill/sleep/meta 三模块
            output.append(section.full_content)
            continue

        if bench.transfer_score >= 0.95 and cap.compression_ratio <= 0.40:
            # 高迁移+可压缩 → 用 distilled 版
            output.append(cap.distilled_content)
        elif bench.transfer_score >= 0.90:
            # 中迁移 → 保留骨架+1示例
            output.append(cap.skeleton + cap.best_example)
        else:
            # 低迁移 → 保留完整
            output.append(section.full_content)

    return SkillMd(output)
```

### Compact 产物结构

```
.skillopt/distill/
├── best_skill_min.md           # 压缩版（部署用）
├── best_skill.md               # 完整版（训练用，保留）
├── capability_map_v{N}.json    # 能力地图
├── benchmark_v{N}.json         # 基准验证结果
├── compact_log_v{N}.jsonl      # 压缩日志（每模块的 before/after token）
└── converge_history.jsonl      # 收敛历史（多轮压缩的分数曲线）
```

---

## 46.5 Rollback-Guard：版本回滚兜底

> **核心铁律**：压缩可能失败。Rollback-Guard 是最后的安全网——分数损失超阈值自动回滚到 best_skill.md，且记录失败原因进 blacklist，下次 Distill 不再尝试该压缩路径。

### Guard 判定逻辑

```
def rollback_guard(best_skill, min_skill, validation_set):
    best_score = evaluate(best_skill, validation_set)
    min_score = evaluate(min_skill, validation_set)

    loss_ratio = (best_score - min_score) / best_score

    if loss_ratio > 0.05:
        # 损失超 5% → 自动回滚
        return GuardResult(
            action="rollback",
            best_score=best_score,
            min_score=min_score,
            loss_ratio=loss_ratio,
            reason=f"loss {loss_ratio:.2%} exceeds 5% threshold",
            blacklist_entry=extract_failed_path(min_skill)
        )
    elif loss_ratio > 0.03:
        # 损失 3%-5% → 警告但接受
        return GuardResult(
            action="accept_with_warning",
            best_score=best_score,
            min_score=min_score,
            loss_ratio=loss_ratio,
            reason=f"loss {loss_ratio:.2%} in warning zone"
        )
    else:
        # 损失 ≤ 3% → 接受
        return GuardResult(
            action="accept",
            best_score=best_score,
            min_score=min_score,
            loss_ratio=loss_ratio,
            reason="loss within tolerance"
        )
```

### 版本回滚三态

| 状态 | 触发条件 | 动作 | 产物 |
|:-----|:---------|:-----|:-----|
| `accept` | loss ≤ 3% | 部署 min 版 | best_skill_min.md 进生产 |
| `accept_with_warning` | 3% < loss ≤ 5% | 部署 min 版 + 标记观察 | min 版 + watch_log |
| `rollback` | loss > 5% | 回滚 best 版 + 黑名单 | best_skill.md + blacklist |

### 回滚黑名单

```json
{
  "blacklist": [
    {
      "ts": "2026-07-25T03:00:00Z",
      "failed_module": "dialogue-mastery",
      "failed_path": "compact MBTI 16 型声线档案",
      "loss_ratio": 0.08,
      "reason": "MBTI 声线是高频调用能力，压缩后群戏对白质量暴跌",
      "ban_until": "v11.0"
    }
  ]
}
```

---

## 46.6 Converge：终态收敛判定

> **核心铁律**：技能不是无限进化的。连续 3 次压缩后 composite_score 无提升（Δ < 0.005）= 收敛。收敛后冻结模块数，不再新增模块，只做内部优化。

### 收敛三判据

```
判据 ①：压缩收敛
  连续 3 次 Compact 的 min_score 提升 < 0.005
  → 标 "compact_converged"

判据 ②：训练收敛
  连续 5 epoch 的 best_score 提升 < 0.01
  → 标 "train_converged"

判据 ③：帕累托收敛
  连续 3 次 Dream-Rollout 无 breakthrough
  → 标 "pareto_converged"

三判据全部命中 → 技能进入"终态"
  - 模块数冻结（v10.0 = 46 个，不再增加）
  - 训练降频（从每章训练改为每周训练）
  - 仅保留 Sleep 离线进化
```

### ConvergeResult Schema

```json
{
  "skill_version": "v10.0",
  "module_count": 46,
  "converge_status": {
    "compact_converged": true,
    "train_converged": true,
    "pareto_converged": true,
    "all_converged": true
  },
  "final_composite_score": 8.47,
  "final_module_count": 46,
  "frozen_at": "2026-07-25T03:30:00Z",
  "next_review": "2026-08-25",
  "modules_frozen": [
    "core-writing", "planning", "world-characters",
    "anti-ai-polish", "plot-engineering", "audit-workflow",
    "style-configuration", "skill-evolution", "sleep-evolution",
    "meta-optimizer", "skill-compaction",
    "..."
  ]
}
```

### 收敛后的训练降频策略

| 阶段 | 训练频率 | Sleep 频率 | Dream 频率 | 备注 |
|:-----|:---------|:----------|:----------|:-----|
| v7.0-v9.0（成长期） | 每章 | 每夜 | 每 5 epoch | 高频迭代 |
| v10.0（收敛期） | 每周 | 每夜 | 每月 | 降频保稳 |
| v11.0+（维护期） | 每月 | 每周 | 季度 | 仅维护 |

---

## 46.7 零成本部署：best_skill_min.md 上线

> **核心铁律**：min 版的目标是"塞进 8k token 上下文窗口"——让任何模型（包括 7B 小模型）都能零成本加载完整技能。

### 部署三档

| 档位 | token 预算 | 模块数 | 适用场景 |
|:-----|:----------|:-------|:---------|
| `full` | 30k+ | 46 | 大模型（Claude/GPT-4） + 长篇创作 |
| `standard` | 16k | 46（压缩） | 中模型（DeepSeek/Qwen） + 日常创作 |
| `minimal` | 8k | 46（极简） | 小模型（7B/13B） + 单章写作 |

### 三档切换规则

```
def select_deploy_tier(model_context_window, task_type):
    if model_context_window >= 100_000 and task_type == "long_form":
        return "full"        # 用 best_skill.md
    elif model_context_window >= 32_000:
        return "standard"    # 用 best_skill_min.md（标准档）
    else:
        return "minimal"     # 用 best_skill_min.md（极简档）+ 按需加载
```

### 极简档（minimal）按需加载策略

```
基础包（恒定加载，~4k token）：
  - 总纲铁律（6条）
  - 任务路由表（精简版）
  - 安全边界（5条）
  - core-writing §1（写正文基础流程）
  - anti-ai-polish §1（L1-L4 门禁骨架）

按需加载（任务触发时加载，~4k token 预算）：
  - 用户说"写对话" → 加载 dialogue-mastery 骨架
  - 用户说"修衔接" → 加载 transitions-causality 骨架
  - 用户说"去AI味" → 加载 anti-ai-polish 完整
  - 用户说"审稿" → 加载 audit-workflow 骨架
  - ...（按路由表触发）
```

---

## 46.8 与 v7/v8/v9 的协同

### 与 v7.0 SkillOpt 六步循环的协同

```
v7.0 六步循环 → 产出 best_skill.md（膨胀）
       │
       ▼
v10.0 Compact → 产出 best_skill_min.md（瘦身）
       │
       ▼
v7.0 下轮训练用 best_skill.md（完整版）
v10.0 部署用 best_skill_min.md（压缩版）
```

### 与 v8.0 Sleep 的协同

```
v8.0 Sleep 夜间进化 → 更新 best_skill.md
       │
       ▼
v10.0 Compact 在 Sleep 后触发 → 同步更新 best_skill_min.md
       │
       ▼
次日用 min 版部署（零成本）
```

### 与 v9.0 Meta-Optimizer 的协同

```
v9.0 多目标优化 → 优化 best_skill.md 的 Q/S/T/R
       │
       ▼
v10.0 Compact 把 T（token 效率）作为压缩核心目标
       │
       ▼
v9.0 验证门 → 同时验证 best 和 min 版
       │
       ▼
min 版若帕累托被 best 支配 → 触发 rollback
```

### 四模块协同矩阵

| 模块 | 训练时机 | 产出文件 | 部署文件 | 频率 |
|:-----|:---------|:---------|:---------|:-----|
| v7.0 skill-evolution | 每章 | best_skill.md | best_skill.md | 高频 |
| v8.0 sleep-evolution | 每夜 | best_skill.md | best_skill.md | 中频 |
| v9.0 meta-optimizer | 每 epoch | best_skill.md + ema | best_skill_ema.md | 中频 |
| v10.0 skill-compaction | 收敛后 | best_skill_min.md | best_skill_min.md | 低频 |

---

## 46.9 完整工作流示例

### 场景：v9.0 训练 10 epoch 后触发 v10.0 压缩

```
[输入]
  best_skill.md = 78k token（v9.0 训练后膨胀）
  训练历史 = 10 epoch，47 个失败样本
  验证集 = 30 章 held-out

[Step ① Distill]
  扫描 46 个模块
  提取 CapabilityMap：
    - 高 support（≥5）：保留骨架
    - 低 support（<5）：标候选删除
  产出 capability_map_v10.json
  预估 compression_ratio = 0.38

[Step ② Cross-Benchmark]
  在 bench_A_long（玄幻长篇）/bench_B_short（短篇虐文）/bench_C_commerce（番茄爆文）上验证
  transfer_score 矩阵：
    - 38 个模块 ≥ 0.95（可压缩）
    - 6 个模块 0.90-0.95（中迁移，保留骨架+1示例）
    - 2 个模块 < 0.90（不压缩，元能力）
  产出 benchmark_v10.json

[Step ③ Compact]
  按四类处理策略产出 best_skill_min.md
  最终 token = 78k × 0.38 = 29.6k（standard 档）
  极简档再压缩到 7.8k（minimal 档）
  产出 compact_log_v10.jsonl

[Step ④ Rollback-Guard]
  在 30 章 held-out 上验证：
    - best_score = 8.52
    - min_score = 8.41
    - loss_ratio = 1.3% ≤ 3% → accept
  产出 GuardResult(action="accept")

[Step ⑤ Converge]
  检查收敛三判据：
    - compact_converged: 连续 3 次提升 < 0.005 ✓
    - train_converged: 连续 5 epoch 提升 < 0.01 ✓
    - pareto_converged: 连续 3 次 Dream 无 breakthrough ✓
  → 三判据全中，技能进入终态
  → 模块数冻结 = 46
  → 训练降频为每周

[输出]
  best_skill_min.md（29.6k token，standard 档）
  best_skill_min.md（7.8k token，minimal 档）
  converge_result_v10.json（终态判定）
  下次 review: 2026-08-25
```

---

## 46.10 触发词与路由

### 触发词

```
- 技能压缩
- skill compaction
- best_skill 压缩
- 蒸馏
- distill
- 跨基准迁移
- cross benchmark
- 版本回滚
- rollback skill
- 零成本部署
- minimal skill
- 蒸馏版
- compact skill
- 技能瘦身
- 知识沉淀
- 收敛判定
- 终态冻结
- 模块数冻结
```

### 路由规则

| 用户说 | 动作 |
|:-------|:-----|
| "压缩技能" / "skill compaction" | 跑完整五阶段（Distill→Cross-Benchmark→Compact→Guard→Converge） |
| "蒸馏技能" / "distill" | 只跑 Distill 阶段，产出 CapabilityMap |
| "跨基准验证" / "cross benchmark" | 只跑 Cross-Benchmark 阶段 |
| "回滚技能" / "rollback skill" | 触发 Rollback-Guard，回滚到上一 best 版本 |
| "零成本部署" / "minimal skill" | 产出 minimal 档（8k token） |
| "查看收敛状态" / "终态判定" | 输出 ConvergeResult |
| "训练降频" / "进入维护期" | 切换到收敛后训练频率 |

---

## 46.11 安全约束

```
🚫 禁止压缩：
  ① 总纲铁律 6 条（删了就失控）
  ② 安全边界 5 条（删了就违规）
  ③ 任务路由表（删了就调度失效）
  ④ 跨规则冲突裁决表（删了就冲突无解）
  ⑤ 元能力模块（skill-evolution/sleep-evolution/meta-optimizer/skill-compaction 自身）

✅ 压缩必须保留：
  ① 每个模块的核心骨架（≤3 行）
  ② 高频调用的能力（support_count ≥ 5）
  ③ 高迁移的能力（transfer_score ≥ 0.95）

🚨 强制回滚：
  ① loss_ratio > 5% → 自动回滚
  ② 任一基准分数 < 0.90 → 该模块不压缩
  ③ 元能力模块压缩 → 拒绝（元能力不可压缩）
```

---

## 46.12 与鲁班结构尺的对照

| 鲁班尺 | 检查项 | v10.0 落实 |
|:-------|:-------|:-----------|
| 结构尺 | 模块数 ≤ 50 | 终态冻结 = 46，符合 |
| 实测尺 | best_skill_min 分数 ≥ best × 0.95 | Rollback-Guard 强制 |
| 活体尺 | 部署后能跑通任务 | Cross-Benchmark 验证 |

---

## 46.13 终态宣告

> v10.0 是技能自进化体系的终态版本。从 v7.0 训练循环 → v8.0 离线进化 → v9.0 多目标优化 → v10.0 压缩收敛，形成完整闭环。
>
> **收敛后**：模块数冻结为 46，训练降频，仅保留 Sleep 离线进化。下一次重大升级（v11.0+）需触发"解冻"流程——证明有新能力无法通过现有 46 模块覆盖，且经元反思五问确认。

```
v7.0 训练 → v8.0 离线 → v9.0 多目标 → v10.0 压缩收敛
   ↑                                          ↓
   └──────────── Sleep 离线进化（每夜）──────────┘
                      （闭环）
```
