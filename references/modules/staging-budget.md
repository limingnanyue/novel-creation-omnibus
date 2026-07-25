# 第54章：暂存与预算（Staging & Budget）

> 适用："暂存预算" "staging budget" "edit staging" "批量提交" "atomic apply" "token 预算" "时间预算" "暂存区" "staging area" "atomic commit"
> 核心理念：v7.0 的 Update 步骤逐个应用 Edit——每个 Edit 立即落 best_skill。问题是：单 Edit 通过验证不代表组合后通过——多个 Edit 可能在 best_skill 中相互冲突/重复/越界。v10.8 引入暂存与预算——把一轮训练产出的所有 Edit 先入暂存区，按 token/时间预算批量、原子地应用，任一冲突则整批回滚。
> 来源：Microsoft SkillOpt v0.2.0 `skillopt/update/staging_budget.py` + `skillopt/prompts/staging_budget.md`

---

## 54.1 总览

> **核心铁律**：Edit 不能"边产边落"——必须先入暂存区，攒到预算阈值后整批原子应用。原子性 = 全成功才落盘，任一失败则整批回滚到 best_skill 上一版本。

### v7.0 即时应用 vs v10.8 暂存预算

| 维度 | v7.0 即时应用 | v10.8 暂存预算 |
|:-----|:-------------|:---------------|
| 应用时机 | 每个 Edit 通过验证门立即落盘 | 攒到预算阈值后整批应用 |
| 冲突检测 | 单 Edit 局部检测 | 整批交叉冲突检测 |
| 原子性 | 无（部分应用可能） | 有（全成功才落盘） |
| 回滚粒度 | 单 Edit 回滚 | 整批回滚 |
| token 预算 | 无 | 显式 token 上限 |
| 时间预算 | 无 | 显式时间上限 |

### 三种预算

```
1. token_budget: 一批 Edit 涉及的 best_skill 改动 token 数上限
   默认: 4000 token（约 best_skill 体积的 5%）

2. time_budget: 一批 Edit 的处理时间上限
   默认: 600s（10 分钟）

3. count_budget: 一批 Edit 的数量上限
   默认: 20 条 Edit

任一预算达上限 → 触发 atomic apply
```

---

## 54.2 暂存区（Staging Area）

### staging.jsonl schema

```json
{
  "staging_id": "staging_42",
  "epoch": 42,
  "edits": [
    {
      "edit_id": "edit_42",
      "op": "REPLACE",
      "target_skill_section": "anti-ai-polish#§3.2-L1-L4-硬门禁",
      "old_text": "...",
      "new_text": "...",
      "source": "skill-aware-reflection",
      "token_delta": 28
    },
    {
      "edit_id": "edit_43",
      "op": "ADD",
      "target_skill_section": "dialogue-mastery#§21.3-节奏控制",
      "new_text": "...",
      "source": "contrastive-reflection",
      "token_delta": 56
    }
  ],
  "cumulative_token_delta": 84,
  "cumulative_time_spent": 120,
  "status": "staging",
  "created_ts": "2026-07-25T03:00:00Z"
}
```

### 暂存区状态机

```
                ┌────────────┐
                │  STAGING   │ ← Edit 入暂存区
                └─────┬──────┘
                      │ 任一预算达上限 OR epoch 结束
                      ▼
                ┌────────────┐
                │  CHECKING  │ ← 整批交叉冲突检测
                └─────┬──────┘
                      │
              ┌───────┴────────┐
              │                │
            无冲突          有冲突
              ▼                ▼
        ┌──────────┐    ┌──────────────┐
        │ APPLYING │    │  CONFLICT    │
        │ 整批应用 │    │  标记+退回   │
        └────┬─────┘    └──────┬───────┘
             │                 │ 修复后重入
             ▼                 ▼
        ┌──────────┐    ┌──────────┐
        │ COMMITTED│    │  STAGING │
        │ 落盘成功 │    └──────────┘
        └──────────┘
             │
             │ 任一 Edit 应用失败
             ▼
        ┌──────────────┐
        │  ROLLED_BACK │ ← 整批回滚到 best_skill 上一版本
        └──────────────┘
```

---

## 54.3 交叉冲突检测

> **核心铁律**：单 Edit 通过验证门不代表组合后通过——必须整批交叉检测。

### 五类冲突

```
① 同段冲突: 两个 Edit 改同一段（old_text 重叠）
   例: edit_A 改 §3.2 L1 句式门禁
       edit_B 也改 §3.2 L1 句式门禁（old_text 与 A 重叠）
   → 拒绝后入者，保留先入者

② 矛盾冲突: 两个 Edit 改不同段但语义相反
   例: edit_A 加"通感虚词即判 AI 味"
       edit_B 删"通感虚词即判 AI 味"
   → 整批退回 CONFLICT，由人工/反思决定保留哪个

③ 累计越界: 多个 Edit 累计 token 超出 best_skill 体积上限
   例: best_skill 当前 8000 token，一批 Edit 累计 +1200 token → 超 9200 上限
   → 拆批：先应用前 N 条达上限，剩余入下一批

④ 引用断裂: 一个 Edit 删除了另一个 Edit 引用的段落
   例: edit_A 删除 §3.5 水分检测段
       edit_B 在 §3.5 水分检测段 ADD 新规则
   → 拒绝 edit_A（保留被引用段）或调整 edit_B 的 target

⑤ 结构破坏: 多个 Edit 累计破坏 best_skill 章节结构
   例: 一批 Edit 删除了 §3/§4/§5 全部段落
   → 整批退回 CONFLICT
```

### 冲突解决策略

```
策略 1 (默认): FIRST_WINS
  先入暂存区的 Edit 保留，后入者拒绝并退回反思

策略 2: HIGH_CONFIDENCE_WINS
  比较两 Edit 的 confidence，高者保留

策略 3: HUMAN_REVIEW
  整批退回 CONFLICT 状态，等待人工裁决

策略 4: AUTO_MERGE
  尝试 LLM 自动合并两 Edit（仅同段且语义相同时）
```

---

## 54.4 原子应用（Atomic Apply）

```
atomic_apply(staging_batch):
  1. 备份 best_skill.md → best_skill.md.bak.{ts}
  2. 逐个应用 staging_batch 中的 Edit
  3. 每应用一个 Edit:
     - 验证 old_text 仍存在（防前一个 Edit 改了同段）
     - 应用 Edit
     - 验证 new_text 落点正确
  4. 若任一 Edit 应用失败:
     - 回滚到 best_skill.md.bak.{ts}
     - 标记整批为 ROLLED_BACK
     - 记录失败原因
     - 触发反思产新 Edit
  5. 全部成功:
     - best_skill 版本号 +1
     - 删除 .bak.{ts}
     - 标记整批为 COMMITTED
```

---

## 54.5 与 v7.0/v10.6/v10.7 的协同

### 与 v7.0 Update 步骤的协同

```
v7.0 Update 步骤入口:
  ↓ 不再即时应用

v10.8 暂存区:
  - 每个通过 v7.0+v10.6+v10.7 验证的 Edit 入暂存区
  - 累计 token/time/count 达预算 → atomic apply

v7.0 Evaluate 步骤:
  - 在 v10.8 COMMITTED 后才跑
  - 评估对象是"应用了整批 Edit 后的 best_skill"
```

### 与 v10.6 技能感知反思的协同

```
v10.8 CONFLICT 状态:
  - 触发 v10.6 技能感知反思
  - failure_signal = "Edit 冲突: edit_A 与 edit_B 在 §3.2 同段冲突"
  - 产新 Edit: 合并两者意图 OR 选择保留其一

v10.8 ROLLED_BACK 状态:
  - 触发 v10.6 反思
  - failure_signal = "原子应用失败: edit_C old_text 不存在"
  - 产新 Edit: 修正 old_text 引用
```

### 与 v10.7 语义密度的协同

```
v10.8 APPLYING 后:
  - 对应用后的 best_skill 跑 v10.7 密度门
  - 若整批 Edit 导致 best_skill 密度下降:
    → 触发 ROLLED_BACK
    → 整批退回，触发反思
```

---

## 54.6 暂存预算日志与审计

### staging_budget_log.jsonl

```json
{
  "staging_id": "staging_42",
  "epoch": 42,
  "edit_count": 12,
  "cumulative_token_delta": 340,
  "cumulative_time_spent": 480,
  "trigger_reason": "count_budget_reached",
  "conflicts_detected": [
    {
      "type": "同段冲突",
      "edits": ["edit_42", "edit_45"],
      "section": "anti-ai-polish#§3.2",
      "resolution": "FIRST_WINS",
      "rejected_edit": "edit_45"
    }
  ],
  "apply_status": "COMMITTED",
  "best_skill_version_before": "v10.6.3",
  "best_skill_version_after": "v10.6.4",
  "ts": "2026-07-25T03:08:00Z"
}
```

### 审计指标

```
暂存预算健康度:
  - atomic_success_rate: 整批原子应用成功率（目标 ≥ 0.9）
  - conflict_rate: 冲突检出率（目标 0.05-0.15，过高=Edit 互相干扰）
  - rollback_rate: 整批回滚率（目标 < 0.1，过高=Edit 质量差）
  - avg_batch_size: 平均每批 Edit 数（目标 8-15）
  - budget_utilization: 预算利用率（目标 0.7-0.9，过低=预算过大）

异常:
  - atomic_success_rate < 0.7 → Edit 间冲突严重，触发 v9.0 元反思
  - rollback_rate > 0.3 → best_skill 已不稳定，触发回滚
  - budget_utilization < 0.3 → 预算过大，调小
```

---

## 54.7 配置

```yaml
# .skillopt/staging-budget.yaml
staging_budget:
  enabled: true
  budgets:
    token: 4000          # 单批 token 上限
    time: 600            # 单批时间上限（秒）
    count: 20            # 单批 Edit 数上限
  trigger_on_epoch_end: true  # epoch 结束强制应用
  atomic_apply: true     # 原子应用
  backup_before_apply: true  # 应用前备份
  conflict_resolution:
    strategy: FIRST_WINS  # FIRST_WINS / HIGH_CONFIDENCE_WINS / HUMAN_REVIEW / AUTO_MERGE
    auto_merge_same_section: true  # 同段同语义自动合并
  density_check_after_apply: true  # 应用后跑 v10.7 密度门
  rollback_on_density_drop: true   # 密度下降触发回滚
```

---

## 54.8 触发词与路由

### 触发词

```
- 暂存预算
- staging budget
- edit staging
- 批量提交
- atomic apply
- token 预算
- 时间预算
- 暂存区
- staging area
- atomic commit
- 整批回滚
- 交叉冲突检测
```

### 路由规则

| 用户说 | 动作 |
|:-------|:-----|
| "看暂存区" / "staging status" | 输出当前暂存区 Edit 数+累计 token+预算利用 |
| "强制应用" / "flush staging" | 立即触发 atomic apply（不等预算达上限） |
| "看冲突" / "conflict log" | 列出最近 N 批的冲突记录 |
| "调预算" | 修改 budgets 配置 |

---

## 54.9 安全约束

```
🚫 禁止：
  ① 跳过暂存区直接应用 Edit（破坏原子性）
  ② 跳过交叉冲突检测直接 atomic apply
  ③ 应用前不备份 best_skill（无法回滚）
  ④ 部分应用失败后不回滚（best_skill 进入半应用状态）
  ⑤ 预算阈值动态修改（避免攻击者放大预算绕过冲突检测）

✅ 必须：
  ① 每个通过验证门的 Edit 必须先入暂存区
  ② 任一预算达上限触发 atomic apply
  ③ 应用前必须备份 best_skill.md.bak.{ts}
  ④ 任一 Edit 应用失败必须整批回滚
  ⑤ 应用后跑 v10.7 密度门，密度下降必须回滚
  ⑥ 冲突必须记录 type+edits+section+resolution+rejected_edit
```
