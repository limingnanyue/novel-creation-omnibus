# 第55章：三向切分门控（3-Way Split Gate）

> 适用："三向切分" "3-way split" "三向门控" "meta hold-out" "meta 验证集" "训练/验证/元验证" "三层隔离" "meta gate" "过拟合检测" "skill 过拟合"
> 核心理念：v7.0 用 70/30 切分（训练/验证）——但验证集被反复用于"判断技能是否提升"，导致 best_skill 隐式过拟合验证集。v10.9 引入三向切分——再多切一份"元验证集"（meta-hold-out），仅用于"判断元过程是否健康"，永不进训练循环，确保 best_skill 的提升是真实的而非对验证集的过拟合。
> 来源：Microsoft SkillOpt v0.2.0 `skillopt/gate/three_way_split.py` + `skillopt/prompts/three_way_split.md`

---

## 55.1 总览

> **核心铁律**：验证集被反复"看"会过拟合——必须再多切一份 meta-hold-out，永不进训练循环，仅在"epoch 结束 / 元反思触发 / Converge 判定"时被一次性查询，作为"真实提升"的最终判据。

### v7.0 二向 vs v10.9 三向

| 维度 | v7.0 二向(70/30) | v10.9 三向(60/20/20) |
|:-----|:-----------------|:---------------------|
| 切分 | train(70%) + val(30%) | train(60%) + val(20%) + meta-hold-out(20%) |
| val 用途 | 训练循环中判断技能提升 | 训练循环中判断技能提升（同 v7.0） |
| meta-hold-out 用途 | 无 | 仅元层判断"是否过拟合 val" |
| 过拟合检测 | 无 | 显式（meta 比 val 差 → 过拟合） |
| Converge 判据 | 仅看 val 收敛 | val 收敛 AND meta 收敛 |
| 数据隔离 | val 不进训练 | val+meta 都不进训练，meta 额外不进反思 |

### 三向切分比例

```
数据集 D = {all_rollouts}

切分:
  D_train (60%): 训练集，进 Rollout/Reflect/Aggregate/Select
  D_val   (20%): 验证集，进验证门（v7.0+v10.6+v10.7+v10.8）
  D_meta  (20%): 元验证集，仅元层查询，永不进训练循环

切分原则:
  ① 三份互不重叠
  ② 切分按时间分层（避免近期数据全部落入某一份）
  ③ 切分后冻结，每 N epoch 才允许重新切分（防反复切分偷看 meta）
  ④ D_meta 的内容在训练日志中不可见（防 LLM 偷看）
```

---

## 55.2 三种门控角色

### ① D_train → 训练循环

```
用途: Rollout/Reflect/Aggregate/Select/Update 全流程
特性: 可反复使用，可进反思 prompt
日志: 训练日志可见
```

### ② D_val → 技能验证门

```
用途: v7.0 验证门+v10.6 段落验证+v10.7 密度门+v10.8 atomic apply 后评估
特性: 不进训练循环，但进验证门（每 epoch 查询）
日志: 验证日志可见（验证分数、密度分数等）
风险: 反复查询 → 隐式过拟合
```

### ③ D_meta → 元验证门

```
用途: 仅以下三种场景查询:
  ① epoch 结束时一次性查询（meta_score）
  ② v9.0 元反思五问触发时查询
  ③ v10.0 Converge 终态判定时查询
特性: 永不进训练循环，永不进反思 prompt
日志: 仅记录 meta_score，不记录 meta 内容（防泄露）
保护: 查询次数受限（每 epoch 最多 1 次）
```

---

## 55.3 过拟合检测

> **核心铁律**：若 D_val 分数持续上升而 D_meta 分数停滞或下降——说明 best_skill 在过拟合 D_val，"提升"是假的。

### 过拟合信号

```
计算最近 N epoch 的趋势:
  val_trend  = linear_regression(D_val scores).slope
  meta_trend = linear_regression(D_meta scores).slope

判定:
  ① 过拟合: val_trend > 0 AND meta_trend ≤ 0
     → best_skill 在 D_val 上"假装"提升
     → 触发 ROLLBACK_TO_N_EPOCHS_AGO（回退到过拟合前）
     → 触发 v9.0 元反思五问

  ② 真提升: val_trend > 0 AND meta_trend > 0
     → 提升是真实的
     → 继续训练

  ③ 双停滞: val_trend ≤ 0 AND meta_trend ≤ 0
     → 训练已收敛或陷入局部最优
     → 触发 v10.5 LR 回升探测

  ④ 异常: val_trend ≤ 0 AND meta_trend > 0
     → D_val 可能被污染或难度异常
     → 触发数据审计
```

### 过拟合回滚

```
if 过拟合信号:
  1. 找到过拟合开始的 epoch（meta_score 最后一次上升的 epoch）
  2. 回退 best_skill 到该 epoch 的版本
  3. 标记过拟合区间所有 Edit 为"过拟合产物"
  4. 进 rejected_edits 缓冲（频次≥3 升级为通用 Edit）
  5. 触发 v9.0 元反思五问
  6. 重新切分 D_val/D_meta（防 LLM 记住旧切分）
```

---

## 55.4 与 v7.0/v9.0/v10.0 的协同

### 与 v7.0 验证门的协同

```
v7.0 验证门入口:
  if rollout ∈ D_train:
    不进验证门（训练集不验证）
  elif rollout ∈ D_val:
    进 v7.0+v10.6+v10.7 验证门（技能验证）
  elif rollout ∈ D_meta:
    不进常规验证门
    仅在元层查询时跑（meta_score）
```

### 与 v9.0 元反思的协同

```
v9.0 元反思五问触发时:
  ① 查询 D_meta 的 meta_score
  ② 比对 D_val 与 D_meta 的趋势
  ③ 若过拟合 → 触发过拟合回滚
  ④ 若双停滞 → 触发 v10.5 LR 回升探测
  ⑤ 元反思日志记录 D_meta 查询次数（防超限）
```

### 与 v10.0 Converge 的协同

```
v10.0 Converge 三判据:
  ① compact_converged: 压缩率稳定
  ② train_converged: D_val 收敛
  ③ pareto_converged: 帕累托前沿稳定

v10.9 增强 Converge:
  + meta_converged: D_meta 也收敛（新增第 4 判据）
  全部 4 判据通过 → 真终态收敛
  仅前 3 判据通过但 meta 未收敛 → "假收敛"，触发过拟合回滚
```

---

## 55.5 切分管理与日志

### three_way_split.json

```json
{
  "split_id": "split_42",
  "epoch": 42,
  "split_ts": "2026-07-25T03:00:00Z",
  "ratios": {"train": 0.6, "val": 0.2, "meta": 0.2},
  "counts": {"train": 60, "val": 20, "meta": 20},
  "freeze_until_epoch": 52,
  "meta_query_count_this_epoch": 0,
  "meta_query_limit_per_epoch": 1,
  "meta_content_visible_in_logs": false,
  "trend_analysis": {
    "window_epochs": 10,
    "val_trend": 0.012,
    "meta_trend": -0.003,
    "signal": "overfitting",
    "action_triggered": "ROLLBACK_TO_EPOCH_38"
  }
}
```

### three_way_split_log.jsonl

```json
{
  "epoch": 42,
  "event": "meta_query",
  "query_reason": "epoch_end",
  "meta_score": 0.78,
  "val_score": 0.85,
  "gap": -0.07,
  "trend_signal": "overfitting",
  "action": "ROLLBACK_TO_EPOCH_38",
  "ts": "2026-07-25T03:08:00Z"
}
```

### 审计指标

```
三向切分健康度:
  - meta_query_rate: D_meta 查询频率（目标 ≤ 1/epoch，超限=偷看）
  - val_meta_gap: D_val 与 D_meta 分数差（目标 |gap| < 0.05，过大=过拟合）
  - overfitting_detection_rate: 过拟合检出率（目标 0-0.1，过高=训练不稳）
  - false_convergence_rate: 假收敛率（前 3 判据过但 meta 未过，目标 < 0.05）
  - split_rotation_rate: 切分轮换频率（目标 每 10 epoch 一次，过频=切分不稳）

异常:
  - meta_query_rate > 1/epoch → D_meta 被偷看，告警
  - val_meta_gap > 0.1 → 严重过拟合，触发回滚
  - false_convergence_rate > 0.1 → Converge 判据失效，重新校准
```

---

## 55.6 配置

```yaml
# .skillopt/three-way-split.yaml
three_way_split:
  enabled: true
  ratios:
    train: 0.6
    val: 0.2
    meta: 0.2
  freeze_epochs: 10  # 切分后冻结 10 epoch
  meta_query:
    limit_per_epoch: 1
    allowed_reasons:
      - epoch_end
      - meta_reflect_trigger  # v9.0
      - converge_check  # v10.0
  trend_window: 10  # 趋势分析窗口
  overfitting:
    val_trend_threshold: 0.005  # val 上升趋势阈值
    meta_trend_threshold: 0.0   # meta 停滞阈值
    action: ROLLBACK_TO_LAST_RISING_EPOCH
  meta_content_in_logs: false  # 日志中不记录 meta 内容
  rotate_split_on_overfit: true  # 过拟合后重新切分
```

---

## 55.7 触发词与路由

### 触发词

```
- 三向切分
- 3-way split
- 三向门控
- meta hold-out
- meta 验证集
- 训练/验证/元验证
- 三层隔离
- meta gate
- 过拟合检测
- skill 过拟合
- 假收敛
- meta_score
```

### 路由规则

| 用户说 | 动作 |
|:-------|:-----|
| "三向切分" / "3-way split" | 输出当前切分比例+冻结状态+各份计数 |
| "看 meta_score" / "meta status" | 输出最近 N epoch 的 meta_score 趋势（不暴露内容） |
| "查过拟合" / "overfitting check" | 计算 val/meta 趋势，输出过拟合信号 |
| "重切分" / "rotate split" | 强制重新切分（需解锁 freeze） |

---

## 55.8 安全约束

```
🚫 禁止：
  ① D_meta 进训练循环（Rollout/Reflect/Aggregate/Select）
  ② D_meta 进反思 prompt（防 LLM 偷看）
  ③ D_meta 查询次数超 limit_per_epoch
  ④ D_meta 内容写入训练日志（仅记录 meta_score）
  ⑤ 切分频率高于 freeze_epochs（防反复切分偷看）
  ⑥ 跳过 meta_converged 直接宣告 Converge（避免假收敛）

✅ 必须：
  ① 三份互不重叠，按时间分层切分
  ② D_meta 仅在三种场景查询（epoch_end/meta_reflect/converge_check）
  ③ 每次查询记录 query_reason + meta_score
  ④ 过拟合信号必须触发回滚
  ⑤ 假收敛必须重新训练
  ⑥ 切分冻结期内不可重切分
```
