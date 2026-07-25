# 第49章：多轮对比反思（Contrastive Reflection）

> 适用："多轮对比反思" "contrastive reflection" "失败 vs 成功" "对照样本" "token 预算" "时间预算" "multi-rollout" "对比反思" "对照组反思" "正负样本对照"
> 核心理念：v7.0 Reflect 只看失败样本，反思容易陷入"修这一个 bug"的局部修补。v10.3 引入多轮对比反思——同时看失败+成功样本，提取"差异特征"作为病灶，让反思产出更通用的 Edit。受 token/时间预算约束，对比数有界。
> 来源：Microsoft SkillOpt v0.2.0 `multi-rollout contrastive reflection under a token/time budget`

---

## 49.1 总览

> **核心铁律**：反思不能只看失败样本——必须同时看同任务的失败+成功 rollout，提取"差异特征"作为病灶。单一失败样本只能产出"修这一处"的局部 Edit；对比反思能产出"修这一类"的通用 Edit。

### 三种反思模式对比

| 模式 | 输入 | 产出 | 适用 |
|:-----|:-----|:-----|:-----|
| 单失败反思（v7.0） | 1 个失败 rollout | 局部 Edit（修这一处） | 简单 bug |
| 单成功反思 | 1 个成功 rollout | 强化 Edit（保留这一招） | 强化已有能力 |
| **对比反思（v10.3）** | 同任务 N 失败 + N 成功 | 通用 Edit（修这一类） | 反复出现的病灶 |

### 对比反思流程

```
┌─────────────────────────────────────────────────────┐
│            多轮对比反思（受 token/时间预算约束）       │
└─────────────────────────────────────────────────────┘

  Step 1: 配对（Pair）
  ──────────────────
  对每个任务 T:
    失败 rollouts: F_T = {f1, f2, ..., fn}
    成功 rollouts: S_T = {s1, s2, ..., sm}
    配对: P_T = {(f1,s1), (f2,s2), ...}（取 min(n,m) 对）

  Step 2: 差异提取（Diff）
  ──────────────────────
  对每对 (fi, si):
    提取差异特征 d_i = diff(fi, si)
    （句式/结构/词汇/节奏/伏笔处理...）

  Step 3: 聚合（Aggregate）
  ─────────────────────
  所有差异聚合: D = {d_1, d_2, ..., d_k}
  频次排序: 高频差异 = 反复出现的病灶

  Step 4: 反思（Reflect）
  ───────────────────
  基于高频差异产出 Edit:
    "在所有 X 场景下，避免 Y，改为 Z"
    （通用规则，而非局部修补）
```

---

## 49.2 Token/时间预算

> **核心铁律**：对比反思受 token/时间预算约束——不能无限对比。预算耗尽即停止配对，进入反思阶段。

### 预算配置

```yaml
# .skillopt/contrastive-budget.yaml
budget:
  token_budget: 50000       # 单次反思总 token 上限
  time_budget_sec: 300       # 单次反思总时间上限（5 分钟）
  max_pairs_per_task: 3      # 每任务最多配对数
  max_tasks_per_epoch: 10    # 每 epoch 最多反思任务数
  rollout_token_cap: 2000    # 单个 rollout 最多看 token 数
```

### 预算耗尽策略

```
配对循环:
  while token_used < token_budget and time_used < time_budget_sec:
    取下一个任务 T
    取 T 的失败+成功 rollouts
    配对 (fi, si)
    提取差异 d_i
    token_used += len(fi) + len(si) + len(d_i)
    pairs_count += 1
    if pairs_count >= max_pairs_per_task:
      break  # 换下一任务

预算耗尽 → 进入反思阶段（用已提取的差异）
```

### 三档预算

| 档位 | token | 时间 | 配对数 | 适用 |
|:-----|:------|:-----|:-------|:-----|
| 快速档 | 20k | 2min | 1对/任务 | 日更紧迫 |
| 标准档 | 50k | 5min | 3对/任务 | 默认 |
| 深度档 | 100k | 15min | 5对/任务 | 周末深度训练 |

---

## 49.3 差异特征提取（Diff）

### 七维差异特征

| 维度 | 含义 | 示例 |
|:-----|:-----|:-----|
| ① 句式 | 失败用陈述长句，成功用对话短句 | 失败"他想起了..."，成功"他猛地抬头：'你！'" |
| ② 结构 | 失败平铺直叙，成功设悬念 | 失败按时间顺序，成功倒叙开头 |
| ③ 词汇 | 失败用 AI 高频词，成功用口语化 | 失败"在这个瞬间"，成功"这会儿" |
| ④ 节奏 | 失败节奏均匀，成功快慢交替 | 失败每段等长，成功长短交错 |
| ⑤ 伏笔处理 | 失败直白点明，成功埋而不点 | 失败"他不知道这是伏笔"，成功只埋不点 |
| ⑥ 信息密度 | 失败信息均匀，成功疏密有致 | 失败每段都推进，成功有喘息段 |
| ⑦ 情绪曲线 | 失败情绪平淡，成功有起伏 | 失败全程低能量，成功先抑后扬 |

### Diff Schema

```json
{
  "pair_id": "P_T_1",
  "task_id": "T",
  "failure_id": "f1",
  "success_id": "s1",
  "diffs": [
    {"dim": "句式", "failure": "陈述长句", "success": "对话短句", "severity": 0.8},
    {"dim": "词汇", "failure": "AI高频词3处", "success": "口语化", "severity": 0.6},
    {"dim": "节奏", "failure": "均匀", "success": "快慢交替", "severity": 0.4}
  ],
  "dominant_diff": "句式",
  "severity_sum": 1.8
}
```

---

## 49.4 聚合与频次排序

> **核心铁律**：单一对比的差异可能是偶发，频次≥3 的差异才是"反复出现的病灶"，值得产出通用 Edit。

### 聚合规则

```
所有差异 D = {d_1, d_2, ..., d_k}

按维度+特征聚合:
  句式_陈述长句 → 出现 5 次（≥3，通用病灶）
  词汇_AI高频词 → 出现 8 次（≥3，通用病灶）
  节奏_均匀 → 出现 2 次（<3，偶发，跳过）

频次排序:
  1. 词汇_AI高频词 (8次)
  2. 句式_陈述长句 (5次)
  3. ...

取 top-3 作为反思焦点
``### 聚合 Schema

```json
{
  "epoch": 42,
  "total_pairs": 15,
  "total_diffs": 47,
  "aggregated": [
    {"feature": "词汇_AI高频词", "freq": 8, "is_recurring": true, "severity_avg": 0.7},
    {"feature": "句式_陈述长句", "freq": 5, "is_recurring": true, "severity_avg": 0.8},
    {"feature": "节奏_均匀", "freq": 2, "is_recurring": false, "severity_avg": 0.4}
  ],
  "focus_top3": ["词汇_AI高频词", "句式_陈述长句"]
}
```

---

## 49.5 通用 Edit 产出

### 通用 Edit vs 局部 Edit

| 类型 | 产出 | 示例 |
|:-----|:-----|:-----|
| 局部 Edit（v7.0） | "修这一处" | "第 12 段的'他不禁想到'改为'他猛地抬头'" |
| **通用 Edit（v10.3）** | "修这一类" | "在所有内心独白场景下，禁用'他不禁想到'，改为动作+对话" |

### 通用 Edit Schema

```json
{
  "edit_id": "E_contrastive_42_1",
  "edit_op": "REPLACE",
  "target_module": "anti-ai-polish.md",
  "scope": "universal",  // vs "local"
  "trigger": {
    "scene": "内心独白",
    "feature": "词汇_AI高频词",
    "freq": 8
  },
  "old": "他不禁想到 / 他暗自思忖 / 在这个瞬间他意识到",
  "new": "动作+对话（如：他猛地抬头：'你！' / 他把烟掐了：'说吧。'）",
  "rationale": "对比反思发现：8/15 失败样本用 AI 高频内心独白词，成功样本全部改为动作+对话",
  "support_count": 8,
  "source": "contrastive_reflection",
  "epoch": 42
}
```

---

## 49.6 与 v7.0/v9.0 的协同

### 与 v7.0 Reflect 的协同

```
v7.0 Reflect（单失败）→ 局部 Edit
       +
v10.3 Contrastive Reflect（多对比）→ 通用 Edit
       │
       ▼
两路 Edit 都进 Aggregate → Select 统一筛选
```

### 与 v9.0 Meta-Optimizer 的协同

```
v9.0 元反思五问（每 10 epoch）→ 检查对比反思健康度:
  - 对比反思产出的 Edit 接受率 vs 单失败 Edit 接受率
  - 如果对比反思接受率显著高 → 增加对比预算
  - 如果对比反思接受率低 → 减少对比预算（投入产出比低）
```

---

## 49.7 触发词与路由

### 触发词

```
- 多轮对比反思
- contrastive reflection
- 失败 vs 成功
- 对照样本
- token 预算
- 时间预算
- multi-rollout
- 对比反思
- 对照组反思
- 正负样本对照
- 通用 Edit
- 频次排序
```

### 路由规则

| 用户说 | 动作 |
|:-------|:-----|
| "对比反思" / "contrastive reflection" | 跑多轮对比反思，输出差异聚合+通用 Edit |
| "查看对比预算" / "contrastive budget" | 输出当前预算配置与剩余 |
| "调整对比档位" / "fast/standard/deep" | 切换三档预算 |

---

## 49.8 安全约束

```
🚫 禁止：
  ① 无预算约束的无限对比（token 爆炸）
  ② 频次<3 的差异产出通用 Edit（偶发误判）
  ③ 对比反思跳过 Aggregate（直接用单对差异）
  ④ 通用 Edit 不标 scope=universal（与局部 Edit 混淆）

✅ 必须：
  ① 受 token/时间预算约束
  ② 频次≥3 才视为反复病灶
  ③ 通用 Edit 标 scope=universal + support_count
  ④ 对比反思与单失败反思并行（不替代）
```
