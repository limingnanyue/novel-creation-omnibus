# 第51章：自主学习率（Autonomous Learning Rate）

> 适用："自主学习率" "autonomous LR" "lr_autonomous" "动态学习率" "accept 率自适应" "学习率自调度" "训练健康度自适应" "LR 衰减" "LR 回升"
> 核心理念：v7.0 学习率预算是三档固定衰减（高/中/低），不随训练状态变化。v10.5 引入自主学习率——根据最近 N epoch 的 accept 率自动调整学习率：accept 率高 → 加大 LR（探索更多）；accept 率低 → 减小 LR（保守稳定）；持续拒绝 → 触发 LR 回升探测（避免陷入局部最优）。
> 来源：Microsoft SkillOpt v0.2.0 `skillopt/optimizer/lr_autonomous.py` + `skillopt/prompts/lr_autonomous.md`

---

## 51.1 总览

> **核心铁律**：学习率不应该是预设的三档固定值——应该随训练健康度自适应。accept 率是训练健康度的直接指标：高 accept = 技能还在快速进化，低 accept = 技能接近收敛或陷入局部最优。

### v7.0 vs v10.5 学习率对比

| 维度 | v7.0 学习率预算 | v10.5 自主学习率 |
|:-----|:----------------|:-----------------|
| 取值 | 三档固定（高0.1/中0.05/低0.02） | 连续自适应（0.001-0.3） |
| 调整 | epoch 衰减（每 10 epoch 降一档） | 基于 accept 率动态调整 |
| 回升 | 无 | 持续拒绝时触发回升探测 |
| 健康度感知 | 无 | 有（accept 率+分数变化） |
| 局部最优逃逸 | 无 | 有（回升探测） |

### 自主学习率公式

```
LR_{t+1} = LR_t × multiplier

multiplier 基于 accept_rate(最近 N epoch):
  accept_rate ≥ 0.6 → multiplier = 1.2  (加大，探索更多)
  0.3 ≤ accept_rate < 0.6 → multiplier = 1.0  (保持)
  0.1 ≤ accept_rate < 0.3 → multiplier = 0.8  (减小，保守)
  accept_rate < 0.1 且持续 ≥ 5 epoch → multiplier = 2.0  (回升探测)

边界:
  LR_min = 0.001 (最小学习率)
  LR_max = 0.3   (最大学习率)
```

---

## 51.2 Accept 率计算

### 滑动窗口

```
最近 N epoch 的 Edit 处理结果:
  N = 10 (默认窗口大小)

accept_count = sum(1 for e in last_N_edits if e.action == "accept")
total_count = len(last_N_edits)
accept_rate = accept_count / total_count

例:
  last_10_edits = [accept, reject, accept, accept, reject, accept, reject, accept, accept, reject]
  accept_count = 6
  accept_rate = 6/10 = 0.6
  → multiplier = 1.2 (加大 LR)
```

### 多维 accept 率

```
不只看总体 accept 率，还按维度看:
  Q_accept_rate: 质量维度 accept 率
  S_accept_rate: 速度维度 accept 率
  T_accept_rate: token 维度 accept 率
  R_accept_rate: 留存维度 accept 率

最差的维度决定 multiplier（短板效应）:
  min(Q, S, T, R) 的 accept_rate 决定 LR
```

---

## 51.3 LR 回升探测

> **核心铁律**：持续低 accept 率（<0.1 持续 5 epoch）可能意味着陷入局部最优——此时不应继续减小 LR，而应回升 LR 探测新区域。

### 回升触发

```
持续低 accept 检测:
  if accept_rate < 0.1 for 5 consecutive epochs:
    trigger LR probe
    
LR probe:
  LR_temp = LR_current × 2.0  (临时加倍)
  跑 3 epoch 探测
  if 探测期 accept_rate > 0.3:
    接受新 LR (逃逸成功)
    record escape_log
  else:
    回退到探测前 LR (逃逸失败)
    record failed_escape_log
    触发 Dream-Rollout (用 v9.0 做更大探索)
```

### 回升日志

```json
{
  "probe_id": "probe_42",
  "trigger_epoch": 42,
  "trigger_reason": "accept_rate<0.1 for 5 epochs",
  "lr_before": 0.005,
  "lr_probe": 0.01,
  "probe_epochs": 3,
  "probe_accept_rate": 0.4,
  "escape_success": true,
  "lr_after": 0.01,
  "ts": "2026-07-25T03:00:00Z"
}
```

---

## 51.4 自主学习率状态机

```
                ┌─────────────┐
                │   NORMAL    │ ← 默认状态
                │ LR 随 accept│
                │ 率自适应    │
                └──────┬──────┘
                       │ accept_rate<0.1 持续5epoch
                       ▼
              ┌─────────────────┐
              │   PROBING       │
              │ LR 临时×2       │
              │ 跑 3 epoch 探测 │
              └────┬───────┬────┘
                   │       │
              探测成功      探测失败
                   ▼       ▼
        ┌──────────┐  ┌──────────────┐
        │ ESCAPED  │  │  STUCK       │
        │ 接受新 LR│  │  回退 LR     │
        │ 回 NORMAL│  │  触发 Dream  │
        └──────────┘  └──────┬───────┘
                             │ Dream 完成
                             ▼
                       ┌──────────┐
                       │  NORMAL  │
                       └──────────┘
```

---

## 51.5 与 v7.0/v9.0 的协同

### 与 v7.0 学习率预算的协同

```
v7.0 三档预算(高/中/低) → 作为 LR 上下界
       │
       ▼
v10.5 自主学习率 → 在 [LR_min, LR_max] 内连续自适应
       │
       ▼
不再每 10 epoch 固定降档，而是随 accept 率动态调整
```

### 与 v9.0 Meta-Optimizer 的协同

```
v9.0 元反思五问(每 10 epoch) → 检查 LR 健康度:
  - LR 是否在合理范围
  - 是否频繁触发回升探测
  - 探测成功率
  - 是否需要调整 LR 边界
```

---

## 51.6 LR 配置与日志

### 配置

```yaml
# .skillopt/lr-autonomous.yaml
lr:
  mode: autonomous  # vs "fixed" (v7.0)
  lr_min: 0.001
  lr_max: 0.3
  window_size: 10  # 滑动窗口
  probe:
    trigger_epochs: 5  # 持续低 accept 触发
    trigger_threshold: 0.1
    probe_epochs: 3
    probe_multiplier: 2.0
    probe_success_threshold: 0.3
  multipliers:
    high_accept: 1.2  # accept≥0.6
    mid_accept: 1.0   # 0.3≤accept<0.6
    low_accept: 0.8   # 0.1≤accept<0.3
    probe: 2.0        # 回升探测
```

### 日志

```json
{
  "epoch": 42,
  "lr_current": 0.012,
  "lr_prev": 0.01,
  "multiplier": 1.2,
  "accept_rate": 0.6,
  "q_accept": 0.7,
  "s_accept": 0.5,
  "t_accept": 0.6,
  "r_accept": 0.4,
  "min_dim_accept": 0.4,
  "state": "NORMAL",
  "ts": "2026-07-25T03:00:00Z"
}
```

---

## 51.7 触发词与路由

### 触发词

```
- 自主学习率
- autonomous LR
- lr_autonomous
- 动态学习率
- accept 率自适应
- 学习率自调度
- 训练健康度自适应
- LR 衰减
- LR 回升
- 回升探测
- 局部最优逃逸
```

### 路由规则

| 用户说 | 动作 |
|:-------|:-----|
| "自主学习率" / "autonomous LR" | 切换到自主学习率模式 |
| "查看 LR 状态" / "lr status" | 输出当前 LR+accept 率+状态机 |
| "触发回升探测" / "lr probe" | 手动触发 LR 回升探测 |

---

## 51.8 安全约束

```
🚫 禁止：
  ① LR 超出 [LR_min, LR_max] 边界
  ② 跳过 accept 率计算直接调 LR
  ③ 回升探测失败后不回退 LR
  ④ 频繁触发回升（每 epoch 触发 → 视为攻击）

✅ 必须：
  ① LR 在 [0.001, 0.3] 内
  ② 滑动窗口 N=10
  ③ 回升探测有日志
  ④ 探测失败触发 Dream-Rollout
```
