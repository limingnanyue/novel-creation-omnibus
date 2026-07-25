# 第45章：多目标元优化器（Meta-Optimizer）

> 适用："多目标优化" "元优化" "meta optimizer" "dream rollout" "慢更新" "SlowUpdate" "EMA" "跨书迁移" "帕累托" "元反思"
> 核心理念：v7.0/v8.0 只优化"质量分数"单目标。v9.0 引入多目标优化——质量 × 速度 × token × 留存四维帕累托前沿，加 epoch 级慢更新 EMA 和 dream-rollout 探索。
> 来源：Microsoft SkillOpt v0.2.0 `SlowUpdateResult` / multi-objective / dream-rollout 实验控制

---

## 45.1 多目标优化总览

> **核心铁律**：技能优化不得只追求质量分数。质量提升但 token 爆炸 / 速度暴跌 / 留存下降的 Edit = 过拟合质量维度，必须 reject。

### 四优化目标

| 目标 | 符号 | 单位 | 方向 | 权重 |
|:-----|:-----|:-----|:-----|:-----|
| 质量分数 | Q | 0-10 | ↑ 越大越好 | 0.40 |
| 速度 | S | 秒/章 | ↓ 越小越好 | 0.25 |
| token 效率 | T | token/章 | ↓ 越小越好 | 0.20 |
| 读者留存 | R | 0-1 | ↑ 越大越好 | 0.15 |

### 加权综合分公式

```
composite_score = 0.40×Q_norm + 0.25×S_norm + 0.20×T_norm + 0.15×R_norm

其中：
  Q_norm = Q / 10
  S_norm = 1 - min(S / S_baseline, 1)        # S_baseline = 历史平均速度
  T_norm = 1 - min(T / T_baseline, 1)        # T_baseline = 历史平均 token
  R_norm = R                                  # 留存率直接归一化
```

### 帕累托前沿判定

```
Edit A 支配 Edit B 当且仅当：
  A 在所有 4 个目标上 ≥ B，且至少 1 个目标严格 >
─────────────────────────────────────────────
🚨 铁律：验证门不仅比对 composite_score，还要检查帕累托支配。
        若新 Edit 被旧 best 支配（任一目标严格劣化），即使 composite_score 略高也 reject。
```

---

## 45.2 Dream-Rollout 探索

> **核心铁律**：Dream-rollout 是"做梦式探索"——在不影响 best_skill 的前提下， speculate 一批激进 Edit，看能否突破当前帕累托前沿。这是 SkillOpt v0.2.0 的实验性控制。

### Dream-Rollout 三步

```
Step 1: Speculate（推测）
  从 rejected_edits 缓冲池 + 高 confidence 模式中
  生成 K 个激进 Edit 组合（K 默认 5）
  每个 Edit 组合 = 多个 Edit 的叠加

Step 2: Rollout（做梦）
  用每个 Edit 组合临时构建 dream_skill
  在 dream 验证集（独立于训练+验证集的第三份）上跑
  记录四目标分数

Step 3: Filter（过滤）
  仅保留帕累托前沿上的 dream_skill
  若某个 dream_skill 严格支配当前 best → 标"breakthrough"
  breakthrough 进入正式训练循环（下轮 epoch 作为候选）
  非 breakthrough 的 dream 结果归档但不应用
```

### Dream-Rollout 与正式训练的区别

| 维度 | 正式训练（v7.0/v8.0） | Dream-Rollout（v9.0） |
|:-----|:---------------------|:---------------------|
| 验证集 | held-out 30% | dream 集（独立第三份） |
| 学习率 | 受衰减规则约束 | 不受约束（允许激进） |
| 失败处置 | 进 rejected_edits | 仅归档，不进缓冲 |
| 应用时机 | 验证门通过即更新 | 仅 breakthrough 才进下轮候选 |
| 频率 | 每 epoch | 每 5 epoch 一次 |

### Dream-Rollout 三纪律

```
1. Dream 集必须独立于训练集和验证集（第三份数据）
2. Dream-rollout 不得直接更新 best_skill（必须经正式训练循环）
3. Dream-rollout 产物归档到 dream_archive/，30 天后清理
─────────────────────────────────────────────
🚨 铁律：Dream-rollout 是探索，不是部署。
        breakthrough dream_skill 必须在正式训练循环中重新验证才可应用。
```

---

## 45.3 SlowUpdate 慢更新 EMA

> **核心铁律**：每个 epoch 结束后做慢更新——对 best_skill 做 EMA（指数移动平均）平滑，防止技能抖动。这是 SkillOpt `SlowUpdateResult` 的核心。

### EMA 公式

```
best_skill_ema(t) = α × best_skill(t) + (1-α) × best_skill_ema(t-1)

其中：
  α = 慢更新系数（默认 0.3）
  α 越小 = 越保守（技能变化越慢）
  α 越大 = 越激进（技能紧跟最新 epoch）
─────────────────────────────────────────────
🚨 铁律：EMA 作用于技能文档的"语义向量"，不是字面文本。
        具体：把 best_skill 编码为 embedding，在 embedding 空间做 EMA，
        然后由 optimizer 模型把 EMA 后的 embedding 解码回文档。
        字面 EMA 无意义（文档不是数值）。
```

### SlowUpdateResult schema（对齐 SkillOpt v0.2.0）

```json
{
  "epoch": 7,
  "alpha": 0.3,
  "ema_applied": true,
  "best_skill_before_ema": "v8.0.3",
  "best_skill_after_ema": "v8.0.4",
  "semantic_drift": 0.12,
  "regularization_term": 0.05,
  "notes": "EMA 平滑了 3 处激进 Edit，保留核心改进"
}
```

### 慢更新三档

| 档位 | α | 适用阶段 | 效果 |
|:-----|:---|:---------|:-----|
| **保守档** | 0.1 | 早期 epoch（v7.0 大改期） | 技能几乎不动，防抖动 |
| **标准档** | 0.3 | 中期 epoch（v8.0 微调期） | 平滑跟进，平衡稳定与进化 |
| **激进档** | 0.5 | 后期 epoch（v9.0+ 精修期） | 快速跟进，接近直接替换 |

### 正则化项

```
regularization = λ × ||best_skill(t) - best_skill_ema(t-1)||

作用：惩罚 best_skill 偏离 EMA 太远（防止单 epoch 巨变）
λ 默认 0.05
─────────────────────────────────────────────
若 regularization > threshold(0.3)：
  → 标"巨变预警"，强制人工 review
  → 同时降级 α 到保守档（0.1）
```

---

## 45.4 元反思（Meta-Reflect）

> **核心铁律**：元反思不是反思章节，而是反思"训练过程本身"——学习率是否合理？缓冲池是否堆积？验证门是否过严？

### 元反思五问

```
每 10 个 epoch 做一次元反思：

① 学习率健康度
   过去 10 epoch 的 accept 率是否在 20%-60%？
   < 20% = 学习率过小或验证门过严 → 考虑升档（但受"只衰不升"约束，需人工裁决）
   > 60% = 学习率过大或验证门过松 → 降档

② 缓冲池健康度
   rejected_edits 缓冲池大小趋势？
   持续增长 = 病灶根因未解决 → 触发 Sleep 深度 Mine
   持续缩小 = 进化收敛 → 可考虑 dream-rollout 突破

③ 帕累托前沿移动
   过去 10 epoch 的四目标前沿是否推进？
   质量提升但 token 爆炸 = 过拟合质量 → 调整权重
   全维停滞 = 收敛 plateau → 考虑跨书迁移

④ 验证门判定分布
   accept/reject/tie 比例？
   tie 过多 = min_delta 过大 → 降低 min_delta
   reject 过多 = Edit 质量差 → 加强 Reflect 阶段

⑤ best_skill 溯源
   当前 best_skill 的 parent 链是否健康？
   频繁回滚 = 训练不稳定 → 暂停训练，先跑 Sleep 巩固
```

### 元反思产物 meta_reflect_log.jsonl

```jsonl
{"reflect_at_epoch":10,"ts":"2026-07-25T05:00:00Z","accept_rate":0.35,"buffer_size":12,"buffer_trend":"stable","pareto_movement":"quality_up_token_stable","gate_dist":{"accept":7,"reject":18,"tie":5},"min_delta_suggestion":"保持0.05","parent_chain_healthy":true,"action":"continue"}
```

---

## 45.5 跨书迁移（Cross-Book Transfer）

> **核心铁律**：跨书迁移不是简单复制 Edit——而是迁移"技能的抽象能力"，在目标书上重新验证。

### 跨书迁移三模式

| 模式 | 迁移内容 | 验证方式 | 风险 |
|:-----|:---------|:---------|:-----|
| **直接迁移** | 完整 Edit（op+content+target） | 目标书验证集 | 高（语感差异可能失效） |
| **抽象迁移** | Edit 的"意图"（非具体文本） | 目标书重新生成具体 Edit | 中（需 optimizer 重新解码） |
| **能力迁移** | 训练好的 sub-skill（如去AI味能力） | 目标书 held-out | 低（能力通用性强） |

### 跨书迁移流程

```
Step 1: 识别可迁移 Edit
  - source_type = "cross_book_transfer"
  - 该 Edit 在源书的 support_count ≥ 5
  - 该 Edit 与具体剧情无关（通用写作能力）

Step 2: 选择迁移模式
  - 题材相近（同 genre_router）→ 直接迁移
  - 题材不同但能力通用 → 能力迁移
  - 题材不同且 Edit 含剧情依赖 → 抽象迁移

Step 3: 目标书验证
  - 在目标书 held-out 验证集上跑
  - composite_score 严格提升（min_delta 0.05）才 accept
  - 失败 → Edit 进源书专属缓冲，不影响目标书

Step 4: 落盘 transfer_log.jsonl
```

### transfer_log.jsonl schema

```jsonl
{"transfer_id":"T-001","ts":"2026-07-25T06:00:00Z","source_book":"ye-ban","target_book":"xiyou","edit_id":"edit_2026_07_25_001","mode":"ability_transfer","source_score_delta":+0.15,"target_score_delta":+0.08,"action":"accept"}
{"transfer_id":"T-002","ts":"2026-07-25T06:30:00Z","source_book":"ye-ban","target_book":"xianxia","edit_id":"edit_2026_07_25_002","mode":"direct_transfer","source_score_delta":+0.12,"target_score_delta":-0.03,"action":"reject","reason":"仙侠题材语感不适配"}
```

---

## 45.6 多目标验证门增强

> **核心铁律**：v7.0 验证门只看质量分数。v9.0 验证门看四目标帕累托 + composite_score。

### 增强版 GateResult

```json
{
  "action": "accept | reject | tie | pareto_dominated",
  "current_skill": "v8.0.3",
  "current_scores": {"Q": 8.5, "S": 45, "T": 12000, "R": 0.72},
  "current_composite": 0.78,
  "new_skill": "v8.0.4",
  "new_scores": {"Q": 8.7, "S": 48, "T": 12500, "R": 0.71},
  "new_composite": 0.79,
  "pareto_comparison": "new dominates old on Q, old dominates new on S/T/R → non-dominated",
  "best_skill": "v8.0.4",
  "best_composite": 0.79,
  "best_step": 7
}
```

### 四种 action 判定

| 情形 | action | 后续 |
|:-----|:-------|:-----|
| new composite > old + min_delta 且 new 帕累托不劣于 old | **accept** | 更新 best |
| new 被旧 best 帕累托支配（任一目标严格劣化） | **pareto_dominated** | reject，Edit 进缓冲 |
| new composite ∈ (old, old+min_delta] | **tie** | 保留候选 |
| new composite ≤ old | **reject** | Edit 进缓冲 |

---

## 45.7 与 v7.0/v8.0 的协同

```
v7.0 日间训练（单目标质量）→ v9.0 元反思（每10 epoch）→ 调整学习率/权重
v8.0 Sleep 夜间巩固 → v9.0 跨书迁移（迁移 Sleep 巩固的能力）
v9.0 Dream-rollout（每5 epoch）→ breakthrough 进 v7.0 正式训练循环
v9.0 SlowUpdate EMA → 每个 epoch 后平滑 best_skill
```

### 协同时序图

```
Epoch 1-4:  v7.0 训练（单目标）+ v9.0 SlowUpdate EMA
Epoch 5:    v9.0 Dream-rollout（首次）+ v7.0 训练 + SlowUpdate
Epoch 6-9:  v7.0 训练 + SlowUpdate
Epoch 10:   v9.0 元反思（首次）+ v7.0 训练 + SlowUpdate
            ↓
夜间:       v8.0 Sleep + v9.0 跨书迁移
            ↓
Epoch 11+:  循环...
```

---

## 45.8 触发词与路由

| 用户说 | 触发动作 |
|:-------|:---------|
| "多目标优化" / "meta optimizer" / "帕累托" | 跑多目标验证门 |
| "dream rollout" / "做梦探索" / "突破探索" | 跑 Dream-Rollout 三步 |
| "慢更新" / "SlowUpdate" / "EMA" | 跑 epoch 级 EMA 平滑 |
| "元反思" / "meta reflect" / "训练健康度" | 跑 10 epoch 元反思五问 |
| "跨书迁移" / "cross book transfer" | 跑跨书迁移流程 |
| "查看帕累托前沿" / "pareto frontier" | 输出当前四目标前沿 |

---

## 45.9 Meta-Optimizer 自检清单

```
□ 四目标是否都采集了？（Q/S/T/R 不得缺一）
□ composite_score 是否按权重公式计算？
□ 帕累托支配是否检查？（不得只看 composite）
□ Dream-rollout 是否用了独立第三份验证集？
□ Dream-rollout 产物是否归档但不直接应用？
□ SlowUpdate EMA 是否在 embedding 空间做？（非字面）
□ α 系数是否符合当前阶段档位？
□ 正则化项 > 0.3 是否触发巨变预警？
□ 元反思是否每 10 epoch 跑一次？
□ 跨书迁移失败是否进源书专属缓冲？
```

---

**版本：v1.0 | 最后更新：2026-07-25 | 集成多目标优化(四维帕累托)+Dream-Rollout探索+SlowUpdate EMA慢更新+元反思五问+跨书迁移三模式+增强版验证门**
**关联模块：** skill-evolution（v7.0 验证门基础）、sleep-evolution（v8.0 跨书迁移源）、audit-workflow（Q 分数源）、state-tracking（跨书状态）、skill-compaction（v10.0 将读取 meta_reflect_log 决定压缩策略）
**来源：** Microsoft SkillOpt v0.2.0 `SlowUpdateResult` / multi-objective / dream-rollout 实验控制适配
