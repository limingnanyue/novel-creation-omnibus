# 第44章：SkillOpt-Sleep 离线自进化引擎

> 适用："夜间自进化" "sleep evolution" "离线训练" "会话收割" "模式挖掘" "任务重放" "技能巩固" "skillopt-sleep"
> 核心理念：夜间离线时复盘过去会话，挖掘反复出现的失败模式，重放代表性任务，在验证门后巩固已验证的技能编辑——不打扰日间写作。
> 来源：Microsoft SkillOpt v0.2.0 `skillopt-sleep` CLI（https://github.com/microsoft/SkillOpt/blob/main/docs/sleep/README.md）

---

## 44.1 Sleep 四阶段总览

> **核心铁律**：Sleep 是 v7.0 六步循环的"夜间离线版"——同样的训练纪律，但跑在历史会话上而非实时章节。Sleep 不替代日间训练，而是补充它。

```
┌─────────────────────────────────────────────────────────────┐
│              SkillOpt-Sleep 夜间离线自进化流水线              │
└─────────────────────────────────────────────────────────────┘

  ① Harvest          ② Mine              ③ Replay
  ────────          ──────              ───────
  收割过去 N 天      挖掘反复出现        重放代表性
  的会话日志          的失败模式          失败任务
       │                │                  │
       ▼                ▼                  ▼
  sessions.jsonl    patterns.json     replay_results.json
                                           │
                                           ▼
                                 ④ Consolidate
                                 ────────────
                                 在验证门后巩固
                                 已验证的技能编辑
                                       │
                                       ▼
                                 best_skill.md（更新或保持）
                                 + sleep_log.jsonl
```

### 四阶段契约表

| # | 阶段 | 输入 | 输出 | 必做动作 | 禁忌 |
|:---|:-----|:-----|:-----|:---------|:-----|
| ① | **Harvest** | 过去 N 天会话 | `sessions.jsonl` | 收集所有章节输出+审计报告+meta_review | 不得只挑高分章节（失败样本更值钱） |
| ② | **Mine** | sessions.jsonl | `patterns.json` | 挖掘重复≥3次的失败模式 | 不得把偶发错误当模式 |
| ③ | **Replay** | patterns.json + best_skill | `replay_results.json` | 重放代表性任务，跑 v7.0 六步循环 | 不得用训练集分数判定（必须 held-out） |
| ④ | **Consolidate** | replay_results + 验证门 | `best_skill.md` + `sleep_log.jsonl` | accept 才更新 best_skill | 不得跳过验证门直接合并 |

---

## 44.2 ① Harvest 会话收割

> **核心铁律**：收割必须包含失败样本。只收割高分章节的 Sleep = 自我感动，不会产生进化。

### Harvest 输入源

| 源 | 路径 | 内容 | 优先级 |
|:---|:-----|:-----|:-------|
| 章节输出 | `chapters/*.md` | 正文文本 | 高 |
| 审计报告 | `.novel_state/<book>/audit/*.json` | E1-E5 findings + 11 维分数 | 高 |
| meta_review_log | `.novel_state/<book>/meta_review_log.jsonl` | 跨会话自省记录 | 高 |
| rejected_edits | `.novel_state/<book>/rejected_edits.jsonl` | v7.0 拒绝编辑缓冲池 | 中 |
| 读者反馈 | `feedback/*.md`（可选） | 评论/弃书点/打赏 | 中 |
| 风格档案 | `style_config.json` | 8 维度配置 + 漂移记录 | 低 |

### sessions.jsonl schema

```jsonl
{"session_id":"sess_2026_07_24_001","ts":"2026-07-24T14:30:00Z","chapter":15,"book_id":"ye-ban","score":8.2,"band":"B","failures":["D2钩子偏弱","D3对白偏离MBTI"],"audit_path":".novel_state/ye-ban/audit/ch15.json"}
{"session_id":"sess_2026_07_24_002","ts":"2026-07-24T16:00:00Z","chapter":16,"book_id":"ye-ban","score":7.5,"band":"C","failures":["D1 AI味命中L2","D6 CT3道具越界"],"audit_path":".novel_state/ye-ban/audit/ch16.json"}
```

### Harvest 时间窗口

```
默认窗口：过去 7 天（可配置 1-30 天）
─────────────────────────────────────────────
🚨 铁律：窗口内会话数 < 10 时，Sleep 自动降级为"仅 Harvest+Mine"，跳过 Replay+Consolidate。
        原因：样本太少，重放结果不可靠，强行巩固会过拟合。
```

---

## 44.3 ② Mine 模式挖掘

> **核心铁律**：模式 = 在≥3个不同会话中出现的同类失败。偶发错误不构成模式，不触发 Replay。

### 模式挖掘三步

```
Step 1: 失败聚类
  对所有 sessions 的 failures 字段做语义聚类
  （用 embedding 或关键词匹配，二选一）

Step 2: 频次过滤
  保留出现次数 ≥ min_support（默认 3）的聚类
  丢弃偶发失败

Step 3: 根因归并
  对每个高频模式，回溯原始 audit 报告，提取根因
  产出 patterns.json
```

### patterns.json schema

```json
{
  "mined_at": "2026-07-25T02:00:00Z",
  "window_days": 7,
  "total_sessions": 21,
  "patterns": [
    {
      "pattern_id": "P-001",
      "failure_type": "D2_钩子偏弱",
      "frequency": 5,
      "sample_sessions": ["sess_001","sess_003","sess_007","sess_012","sess_018"],
      "root_cause": "章末钩子停留在'情感悬念型'，未升级为'危机悬念型'",
      "representative_session": "sess_007",
      "suggested_edit": {
        "op": "REPLACE",
        "target": "references/modules/plot-engineering.md#章末钩子4型",
        "content": "（强化危机悬念型的判定阈值，要求 B5 假象胜利后必须埋危机钩子）"
      },
      "confidence": 0.85
    }
  ]
}
```

### 模式挖掘审计清单

```
□ 模式频次是否≥3？（防止偶发错误被当模式）
□ 根因是否回溯到原始 audit？（不能凭空归因）
□ representative_session 是否选了最典型的那个？
□ confidence < 0.5 的模式是否标记为"低置信，仅供参考"？
□ 是否有互斥模式？（同 target 的 ADD+DELETE 同时出现→冲突，需人工裁决）
```

---

## 44.4 ③ Replay 任务重放

> **核心铁律**：Replay 不是简单重跑旧章节——而是用当前 best_skill 重跑代表性失败任务，看新模式是否复现。若不复现=已解决；若仍复现=需 Edit。

### Replay 执行流程

```
Step 1: 从 patterns.json 取每个模式的 representative_session
Step 2: 加载该 session 的原始输入（章节任务+上下文约束）
Step 3: 用当前 best_skill 重跑（v7.0 六步循环的 Rollout 阶段）
Step 4: 比对新结果 vs 原始失败
        ├─ 失败消失 → 标"resolved"
        ├─ 失败仍在 → 标"persistent"，进入 Reflect 产出 RawPatch
        └─ 新失败出现 → 标"regression"，进 rejected_edits 缓冲
Step 5: 汇总所有 replay 结果
```

### replay_results.json schema

```json
{
  "replayed_at": "2026-07-25T03:00:00Z",
  "best_skill_version": "v7.0.3",
  "results": [
    {
      "pattern_id": "P-001",
      "session_replayed": "sess_007",
      "original_failure": "D2_钩子偏弱",
      "new_outcome": "persistent",
      "new_score": 7.8,
      "score_delta": +0.3,
      "raw_patch": {
        "edits": [
          {
            "op": "REPLACE",
            "target": "references/modules/plot-engineering.md#章末钩子4型",
            "content": "..."
          }
        ],
        "reasoning": "钩子判定阈值过宽，需强化危机悬念型要求"
      }
    }
  ],
  "summary": {"resolved": 2, "persistent": 3, "regression": 0}
}
```

### Replay 三态判定

| 新结果 | 判定 | 后续动作 |
|:-------|:-----|:---------|
| 失败消失 | **resolved** | 模式标记为已解决，不产 Edit |
| 失败仍在 | **persistent** | 产 RawPatch，进 Consolidate |
| 新失败出现 | **regression** | Edit 进 rejected_edits 缓冲（v7.0） |

---

## 44.5 ④ Consolidate 技能巩固

> **核心铁律**：Consolidate 必须跑验证门。即使 Sleep 产出的 Edit 看起来很合理，验证门不通过就 reject。

### Consolidate 执行流程

```
Step 1: 收集所有 persistent 模式的 RawPatch
Step 2: Aggregate（合并去重，同 v7.0 Step 3）
Step 3: Select（按学习率截断，同 v7.0 Step 4）
Step 4: Update（应用 Patch 到 best_skill，产出 new_skill）
Step 5: Evaluate（在 held-out 验证集上跑，同 v7.0 Step 6-8）
Step 6: Gate 判定
        ├─ accept → 更新 best_skill，清空对应缓冲
        ├─ reject → Edit 进 rejected_edits，回滚
        └─ tie → 保留候选，下轮 Sleep 再试
Step 7: 落盘 sleep_log.jsonl
```

### sleep_log.jsonl schema

```jsonl
{"sleep_id":"sleep_2026_07_25","ts":"2026-07-25T04:00:00Z","window_days":7,"sessions_harvested":21,"patterns_mined":4,"replayed":4,"resolved":2,"persistent":3,"regression":0,"gate_action":"accept","best_skill_before":"v7.0.3","best_skill_after":"v7.0.4","score_delta":+0.15,"edits_applied":2}
```

### Consolidate 与 v7.0 的关系

```
v7.0 日间训练：单 epoch，单书籍，实时章节
v8.0 Sleep 夜间巩固：跨 N 天会话，跨书籍（可选），历史重放
─────────────────────────────────────────────
🚨 铁律：Sleep 不得与日间训练同时运行。
        Sleep 启动前必须确认 v7.0 训练循环已结束（无 in_progress 的 epoch）。
        否则会出现 best_skill 写冲突。
```

---

## 44.6 Sleep 调度与触发

### 三种触发方式

| 方式 | 触发条件 | 适用场景 |
|:-----|:---------|:---------|
| **定时触发** | 每日凌晨 02:00（cron） | 常规夜间自进化 |
| **手动触发** | 用户说"跑一次 sleep" / "夜间巩固" | 主动复盘 |
| **阈值触发** | rejected_edits 缓冲池 > 50 条 | 缓冲池膨胀，需 Sleep 清理 |

### Sleep 前置检查

```
□ 当前是否在日间训练中？（是→拒绝启动 Sleep）
□ 过去 N 天会话数是否≥10？（否→降级为仅 Harvest+Mine）
□ best_skill.meta.json 是否存在？（否→Sleep 无法跑，需先初始化）
□ 磁盘空间是否充足？（Sleep 产物约 5-20MB/次）
□ 验证集是否与上次日间训练一致？（不一致→结果不可比）
```

### Sleep 降级策略

| 情形 | 降级动作 | 原因 |
|:-----|:---------|:-----|
| 会话数 < 10 | 仅 Harvest+Mine，跳过 Replay+Consolidate | 样本不足 |
| 磁盘空间不足 | 跳过 Replay（最耗空间），仅 Mine+Consolidate 已有缓冲 | 空间约束 |
| 验证集被污染 | 整轮 Sleep 作废，仅产出 Harvest 报告 | 数据完整性 |
| 日间训练未结束 | 拒绝启动，等待日间训练完成 | 写冲突 |

---

## 44.7 跨书籍 Sleep（可选高级模式）

> 默认 Sleep 单书籍运行。跨书籍 Sleep 是高级模式，需显式开启。

### 跨书籍模式迁移

```
书籍 A 的失败模式 → 提炼为通用 Edit → 在书籍 B 的验证集上检验
                                              │
                                   ┌──────────┴──────────┐
                                   ▼                      ▼
                              accept（迁移成功）      reject（迁移失败）
                                   │                      │
                                   ▼                      ▼
                            更新 best_skill         Edit 进书籍 A 专属缓冲
                            （全局生效）            （不影响书籍 B）
```

### 跨书籍迁移三条件

```
① 两本书题材相近（genre_router 命中同一题材）
② 失败模式与书籍无关（如"章末钩子偏弱"是通用问题，非特定剧情）
③ 在目标书籍验证集上严格提升（min_delta 0.05）
─────────────────────────────────────────────
🚨 铁律：跨书籍迁移失败时，不得强行合并。
        不同书籍的"语感"差异可能让通用 Edit 在某本书上变差。
```

---

## 44.8 Sleep 产物归档

### 归档目录结构

```
.novel_state/<book-id>/sleep/
├── sleep_2026_07_25/
│   ├── sessions.jsonl              # ① Harvest 产物
│   ├── patterns.json               # ② Mine 产物
│   ├── replay_results.json         # ③ Replay 产物
│   ├── consolidate_patch.json      # ④ Consolidate 产物
│   ├── gate_result.json            # 验证门结果
│   └── sleep_log_entry.json        # 单次 Sleep 摘要
├── sleep_2026_07_26/
│   └── ...
└── sleep_history.jsonl             # 历史索引（每次 Sleep 一行）
```

### sleep_history.jsonl

```jsonl
{"sleep_id":"sleep_2026_07_25","ts":"2026-07-25T04:00:00Z","action":"accept","delta":+0.15,"patterns_resolved":2}
{"sleep_id":"sleep_2026_07_26","ts":"2026-07-26T04:00:00Z","action":"reject","delta":-0.05,"patterns_resolved":0}
```

### 归档保留策略

```
- 最近 30 次 Sleep 完整保留
- 30-90 次仅保留 sleep_log_entry.json（摘要）
- 90 次以上删除（可从 git 历史恢复）
─────────────────────────────────────────────
🚨 铁律：accept 的 Sleep 产物永不删除（作为 best_skill 溯源依据）。
        reject 的 Sleep 产物 30 天后可清理。
```

---

## 44.9 与 v7.0 的协同

| 协同点 | v7.0 日间训练 | v8.0 Sleep 夜间巩固 |
|:-------|:-------------|:-------------------|
| 数据源 | 实时章节 | 历史 session |
| 频率 | 按需（用户触发） | 每日凌晨 / 阈值触发 |
| 学习率 | 当前 epoch 档位 | 继承日间最新档位 |
| 验证集 | 当本书 held-out | 当本书 held-out（同一份） |
| rejected_edits | 写入缓冲池 | 读取+清理缓冲池 |
| best_skill | 实时更新 | Sleep 后更新 |
| meta_review_log | 单章自省 | 跨会话自省聚合 |

### 协同时序

```
日间：用户写章 → v7.0 训练 → 更新 best_skill → 落盘 meta_review_log
夜间：Sleep 启动 → Harvest 日间产物 → Mine 模式 → Replay → Consolidate
      → 验证门判定 → 更新（或保持）best_skill → 落盘 sleep_log
次日：用户写章 → 读取最新 best_skill（含 Sleep 巩固） → ...
```

---

## 44.10 触发词与路由

| 用户说 | 触发动作 |
|:-------|:---------|
| "夜间自进化" / "sleep evolution" / "跑一次 sleep" | 启动完整四阶段 Sleep |
| "会话收割" / "harvest sessions" | 仅跑 ① Harvest |
| "模式挖掘" / "mine patterns" | 仅跑 ② Mine（需先 Harvest） |
| "任务重放" / "replay failures" | 仅跑 ③ Replay（需先 Mine） |
| "技能巩固" / "consolidate skill" | 仅跑 ④ Consolidate（需先 Replay） |
| "查看 sleep 历史" / "sleep history" | 输出 sleep_history.jsonl 摘要 |

---

## 44.11 Sleep 自检清单

```
□ Sleep 启动前是否确认日间训练已结束？
□ 过去 N 天会话数是否≥10？（否则降级）
□ Harvest 是否包含失败样本？（不能只挑高分）
□ Mine 的模式频次是否≥3？
□ Replay 是否用了 held-out 验证集？
□ Consolidate 是否跑了验证门？
□ sleep_log.jsonl 是否落盘？
□ accept 的 Sleep 产物是否完整归档？
□ 跨书籍迁移是否满足三条件？
□ Sleep 产物是否按保留策略清理？
```

---

**版本：v1.0 | 最后更新：2026-07-25 | 集成 SkillOpt-Sleep 四阶段（Harvest→Mine→Replay→Consolidate）+ 跨书籍迁移 + 降级策略 + 归档保留**
**关联模块：** skill-evolution（v7.0 六步循环基础）、audit-workflow（Harvest 数据源）、state-tracking（跨会话状态）、meta-optimizer（v9.0 元反思将读取 sleep_log）
**来源：** Microsoft SkillOpt v0.2.0 `skillopt-sleep` CLI（https://github.com/microsoft/SkillOpt/blob/main/docs/sleep/README.md）
