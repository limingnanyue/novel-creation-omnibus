# 第43章：技能自进化引擎（SkillOpt 训练循环）

> 适用："技能进化" "自进化" "skill evolution" "训练技能" "优化技能" "skill-opt" "验证门" "学习率预算" "拒绝编辑缓冲"
> 核心理念：把技能文档当作可训练状态，用深度学习的纪律优化它——epoch/batch/learning-rate/validation-gate，但不碰模型权重。
> 来源：Microsoft SkillOpt v0.2.0（https://github.com/microsoft/SkillOpt）方法论集成

---

## 43.1 SkillOpt 六步训练循环总览

> **核心铁律**：技能文档（SKILL.md + 模块文件）是冻结 agent 的可训练状态。每次进化必须跑完六步循环，缺一步即视为"手工修补"，不算训练。

```
┌─────────────────────────────────────────────────────────────┐
│                  SkillOpt 训练循环（单 epoch）                 │
└─────────────────────────────────────────────────────────────┘

  ① Rollout        ② Reflect        ③ Aggregate
  ─────────        ─────────        ──────────
  用当前技能跑      分析失败样本      汇总成 Patch
  N 个章节任务      提取病灶          （EditOp 集合）
       │                │                │
       ▼                ▼                ▼
  RolloutResult    RawPatch         Patch
                                      │
                                      ▼
  ⑥ Evaluate ◀──────────── ⑤ Update
  ──────────                  ──────
  验证门比对                   应用 Patch 到
  held-out 章节                技能文档
  GateResult                   best_skill.md
       │
       ▼
  accept / reject
  （拒绝进 buffer）
```

### 六步循环契约表

| # | 阶段 | 输入 | 输出 | 必做动作 | 禁忌 |
|:---|:-----|:-----|:-----|:---------|:-----|
| ① | **Rollout** | 当前 skill + 训练 batch | `RolloutResult[]` | 跑 batch_size 个章节任务，记录分数+失败样本 | 不得跳过失败样本采集 |
| ② | **Reflect** | 失败 RolloutResult | `RawPatch` | 错误分析师提取病灶→建议 Edit | 不得直接改技能，只能产出建议 |
| ③ | **Aggregate** | 多个 RawPatch | `Patch` | 去重/冲突消解/合并同源 Edit | 不得丢弃高 support_count 的 Edit |
| ④ | **Select** | Patch + 学习率预算 | `Patch`（精简版） | 按 learning_rate 截断 Edit 数量 | 不得超出预算（防过拟合） |
| ⑤ | **Update** | 精简 Patch + skill.md | 新 skill.md | 应用 ADD/DELETE/REPLACE | 不得越界编辑（只能动 target 指定区域） |
| ⑥ | **Evaluate** | 新 skill + held-out batch | `GateResult` | 比对新旧分数，accept/reject | 不得用训练集分数判定 |

---

## 43.2 EditOp 有界编辑三操作

> **核心铁律**：技能进化只能用三种原子操作，不得整文件重写。这是"有界编辑"的根基——保证可回滚、可审计、可拒绝。

### 三操作定义

| EditOp | 含义 | target 约束 | content 约束 |
|:-------|:-----|:-----------|:-------------|
| **ADD** | 新增内容到指定区域 | target 必须是已存在的锚点（章节号/小节号） | content 必须是完整可独立成立的小节 |
| **DELETE** | 删除指定区域 | target 必须精确到小节级（不得整章删除） | content 为空 |
| **REPLACE** | 替换指定区域 | target 必须精确到小节级 | content 必须比原内容更精炼或更准确 |

### Edit 完整 schema（对齐 SkillOpt v0.2.0）

```json
{
  "op": "ADD | DELETE | REPLACE",
  "content": "新增/替换后的完整文本",
  "target": "references/modules/anti-ai-polish.md#L4-量化指标层",
  "support_count": 3,
  "source_type": "failure_pattern | expert_suggestion | cross_book_transfer",
  "merge_level": "section | paragraph | line",
  "update_origin": "epoch_07_step_02_reflect",
  "update_target": "anti-ai-polish"
}
```

### 有界编辑五条纪律

```
1. target 必须可定位（章节号+小节号+行号锚点）
2. ADD 不得在未读完原文的情况下新增（避免重复）
3. DELETE 必须先确认该小节无其他模块交叉引用
4. REPLACE 必须保留原小节的"功能位"（不能把"铁律"改成"建议"）
5. 单次 Patch 的 Edit 数量 ≤ learning_rate × batch_size
```

---

## 43.3 验证门（Validation Gate）

> **核心铁律**：新技能只在 held-out 验证集上严格优于旧技能时才 accept。否则 reject 进缓冲。这是防止"训练集过拟合"的最后一道闸门。

### GateResult 完整 schema

```json
{
  "action": "accept | reject | tie",
  "current_skill": "skill_v6.2.md",
  "current_score": 8.55,
  "best_skill": "skill_v6.2.md",
  "best_score": 8.55,
  "best_step": 0
}
```

### 验证门判定规则

| 情形 | action | 后续动作 |
|:-----|:-------|:---------|
| 新分数 > 旧分数 + min_delta(0.05) | **accept** | 更新 best_skill，清空该 Edit 的拒绝缓冲 |
| 新分数 ≤ 旧分数 | **reject** | Edit 进拒绝缓冲，回滚到 best_skill |
| 新分数 ∈ (旧分数, 旧分数+min_delta] | **tie** | 不更新 best，但保留 Edit 作为候选（下轮再试） |

### held-out 验证集构建

```
训练集（70%）：近 30 章中随机抽 21 章，用于 Rollout+Reflect
验证集（30%）：剩余 9 章，仅用于 Evaluate 阶段
─────────────────────────────────────────────
🚨 铁律：验证集章节在训练阶段"不可见"。
        一旦发现训练阶段偷读验证集，整轮 epoch 作废。
```

### 五维验证分数

| 维度 | 权重 | 来源 |
|:-----|:-----|:-----|
| D1 语感/去AI | 0.30 | E1 专家 + L1-L4 硬门禁 |
| D2 钩子+节拍 | 0.25 | E2 专家 + Dramatica 定位 |
| D3 人物+对白 | 0.20 | E3 专家 + MBTI 声线 |
| D4 一致性CT | 0.15 | E4 专家 + 16 维快照 |
| D5 商业+风格 | 0.10 | E5 专家 + 风格漂移检测 |

> **注**：验证门分数 ≠ 五专家审计分数。验证门用"精简五维"快速判定，审计用完整 11 维。验证门追求速度（单章 < 30 秒），审计追求精度（单章 5-10 分钟）。

---

## 43.4 学习率预算（Textual Learning Rate）

> **核心铁律**：每个 epoch 的编辑量受学习率约束。学习率过大→技能抖动；过小→收敛太慢。

### 学习率三档

| 档位 | learning_rate | 单 epoch 最大 Edit 数 | 适用阶段 |
|:-----|:--------------|:---------------------|:---------|
| **快档** | 0.3 | batch_size × 0.3 | 早期 epoch（v6.2→v7.0 大改） |
| **中档** | 0.15 | batch_size × 0.15 | 中期 epoch（v7.0→v8.0 微调） |
| **慢档** | 0.05 | batch_size × 0.05 | 后期 epoch（v9.0+ 精修） |

### 学习率衰减规则

```
epoch 1-3:   快档（0.3）   ← 大改，允许新增模块/重写小节
epoch 4-6:   中档（0.15）  ← 微调，只允许 REPLACE 行级
epoch 7+:    慢档（0.05）  ← 精修，只允许 REPLACE 词级
─────────────────────────────────────────────
🚨 铁律：学习率只能衰减，不能回升。
        一旦发现"为加速而调高学习率"，整轮训练作废。
```

### 预算超支处置

```
若 Select 阶段产出的 Edit 数 > learning_rate × batch_size：
  → 按 support_count 降序保留前 N 个
  → 其余 Edit 进下轮候选池（不丢弃，延后处理）
  → 在 Patch.reasoning 中记录"截断原因"
```

---

## 43.5 拒绝编辑缓冲（Rejected-Edit Buffer）

> **核心铁律**：被验证门 reject 的 Edit 不丢弃，进缓冲池。下轮 epoch 优先重试高 support_count 的缓冲 Edit——但若连续 3 轮被拒，永久移除。

### 缓冲池 schema

```json
{
  "buffer_path": ".novel_state/<book-id>/rejected_edits.jsonl",
  "records": [
    {
      "edit_id": "edit_2026_07_25_001",
      "edit": { "op": "REPLACE", "target": "...", "content": "..." },
      "rejected_at_epoch": 3,
      "rejected_reason": "验证集 D1 下降 0.3（去AI味变差）",
      "retry_count": 1,
      "status": "buffered | retried | permanent_drop"
    }
  ]
}
```

### 缓冲池三态迁移

```
buffered ──(下轮 epoch 开始)──▶ retried
   │                              │
   │                              ├─(accept)─▶ promoted（移出缓冲）
   │                              ├─(reject, retry<3)─▶ buffered
   │                              └─(reject, retry≥3)─▶ permanent_drop
   │
   └─(连续 3 轮未被 Select 选中)─▶ permanent_drop
```

### 缓冲池审计清单

```
□ 缓冲池大小是否持续膨胀？（>50 条 = 学习率过小或验证门过严）
□ 高 support_count 的 Edit 是否被反复重试？（说明病灶根因未解决）
□ permanent_drop 的 Edit 是否记录了"放弃原因"？（供后续复盘）
□ 缓冲池中是否有"互斥 Edit"？（同 target 的 ADD+DELETE 不可同时重试）
```

---

## 43.6 best_skill.md 版本管理

> **核心铁律**：始终保留 best_skill.md 作为部署产物。每次 accept 后更新，每次 reject 后回滚。best_skill 是唯一可部署的技能版本。

### 版本目录结构

```
.novel_state/<book-id>/skill_versions/
├── best_skill.md                    # 当前最佳（部署用）
├── best_skill.meta.json             # 版本元数据
├── epoch_001/
│   ├── skill_before.md              # 训练前
│   ├── skill_after.md               # 训练后（可能未 accept）
│   ├── patch.json                   # 本轮 Patch
│   ├── gate_result.json             # 验证门结果
│   └── rollout_results.jsonl        # 训练集 rollout 记录
├── epoch_002/
│   └── ...
└── rejected_edits.jsonl             # 拒绝编辑缓冲池
```

### best_skill.meta.json schema

```json
{
  "version": "v6.2.3",
  "best_score": 8.55,
  "best_step": 7,
  "accepted_at": "2026-07-25T12:00:00Z",
  "parent_version": "v6.2.2",
  "patch_applied": "epoch_007/patch.json",
  "validation_score_breakdown": {
    "D1": 8.5, "D2": 9.0, "D3": 8.5, "D4": 9.5, "D5": 8.0
  },
  "rollback_path": "epoch_006/skill_after.md"
}
```

---

## 43.7 训练循环执行流程（完整版）

```
输入：当前 best_skill.md + 训练集 + 验证集 + 学习率档位
输出：新 best_skill.md（或保持不变）+ 训练日志

──────────────────────────────────────────────────────────────
Step 0: 加载 best_skill.md 作为 current_skill
Step 1: BatchSpec(phase="train", split="train", batch_size=21, seed=epoch)
Step 2: Rollout —— 用 current_skill 跑 21 个训练章节
        记录每个 RolloutResult（分数+失败样本）
Step 3: Reflect —— 对失败样本跑错误分析师
        产出 RawPatch（含建议 Edit + 病灶分析）
Step 4: Aggregate —— 合并多个 RawPatch
        去重/冲突消解/合并同源
        产出 Patch（Edit 集合）
Step 5: Select —— 按 learning_rate 截断
        保留 support_count 前 N 的 Edit
        优先重试缓冲池中 retry_count<3 的 Edit
Step 6: Update —— 应用 Patch 到 current_skill
        产出 new_skill.md（仅 ADD/DELETE/REPLACE）
Step 7: BatchSpec(phase="eval", split="eval", batch_size=9, seed=epoch)
Step 8: Evaluate —— 用 new_skill 跑 9 个验证章节
        计算 five-dim score
Step 9: Gate —— 比对 new_score vs best_score
        若 new_score > best_score + 0.05：
            accept → 更新 best_skill.md，清空对应缓冲
        否则：
            reject → Edit 进缓冲池，回滚到 best_skill.md
Step 10: 落盘 epoch_NNN/ 目录 + 更新 best_skill.meta.json
──────────────────────────────────────────────────────────────
🚨 训练纪律：
   - 单 epoch 不得跨书籍（一本书一个训练上下文）
   - 验证集章节不得在 Step 2-6 阶段被读取
   - 学习率不得在本轮 epoch 中途修改
   - 拒绝的 Edit 必须落盘（不得只存内存）
```

---

## 43.8 与现有模块的联动

| 联动模块 | 联动点 | 数据流 |
|:---------|:-------|:-------|
| `audit-workflow` | Reflect 阶段调用五专家 | 失败样本 → E1-E5 审计 → RawPatch |
| `anti-ai-polish` | Rollout 阶段跑 L1-L4 | 章节输出 → 硬门禁 → D1 分数 |
| `plot-engineering` | Reflect 阶段跑节拍审计 | 章节输出 → Dramatica 定位 → D2 分数 |
| `dialogue-mastery` | Reflect 阶段跑 MBTI 声线 | 章节输出 → 声线判定 → D3 分数 |
| `narrative-weaving` | Evaluate 阶段跑 16 维快照 | 章节输出 → CT 检查 → D4 分数 |
| `style-configuration` | Evaluate 阶段跑漂移检测 | 章节输出 → 漂移 → D5 分数 |
| `state-tracking` | 跨 epoch 状态保存 | best_skill + 缓冲池 + 版本目录 |

---

## 43.9 触发词与路由

| 用户说 | 触发动作 |
|:-------|:---------|
| "训练技能" / "自进化" / "skill evolution" | 跑单 epoch 训练循环 |
| "验证门检查" / "validation gate" | 仅跑 Evaluate 阶段 |
| "回滚技能" / "rollback skill" | 回滚到 best_skill 上一版本 |
| "查看缓冲池" / "rejected edits" | 输出 rejected_edits.jsonl 摘要 |
| "学习率调整" / "learning rate" | 调整下一轮 epoch 的学习率档位 |

---

## 43.10 SkillOpt 集成自检清单

```
□ best_skill.md 是否存在且可部署？
□ best_skill.meta.json 是否记录了 parent_version + rollback_path？
□ 训练集/验证集是否严格隔离？（70/30）
□ 当前 epoch 的学习率档位是否符合衰减规则？
□ 拒绝编辑缓冲池是否落盘？
□ 高 support_count 的缓冲 Edit 是否被优先重试？
□ 验证门判定是否用了 min_delta(0.05)？
□ 单 epoch 是否跨了书籍？（应为否）
□ EditOp 是否仅用了 ADD/DELETE/REPLACE？
□ target 锚点是否精确到小节级？
```

---

**版本：v1.0 | 最后更新：2026-07-25 | 集成 SkillOpt v0.2.0 六步训练循环 + EditOp 有界编辑 + 验证门 + 学习率预算 + 拒绝编辑缓冲 + best_skill 版本管理**
**关联模块：** audit-workflow（Reflect 阶段）、anti-ai-polish（Rollout D1）、plot-engineering（D2）、dialogue-mastery（D3）、narrative-weaving（D4）、style-configuration（D5）、state-tracking（跨 epoch 状态）、sleep-evolution（夜间离线进化）
**来源：** Microsoft SkillOpt v0.2.0（https://github.com/microsoft/SkillOpt）方法论适配
