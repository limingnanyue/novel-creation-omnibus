# 第48章：Handoff Backend 交接后端（Sleep 无模型离线模式）

> 适用："handoff backend" "交接后端" "无模型 Sleep" "无 API key Sleep" "PROMPTS.md" "pending.json" "exit code 3" "fresh-context subagent" "保护 held-out gate" "/skillopt-sleep-handoff" "无凭证自进化"
> 核心理念：v8.0 Sleep 依赖模型 API 调用，对无凭证/无网络/隐私敏感场景不可用。v10.2 引入 Handoff Backend——Sleep 引擎把每个待答的模型调用写到 PROMPTS.md / pending.json（exit code 3 退出），用户的本地 agent session 把答案写到 answers/<id>.md，重跑同命令即可从答案无状态恢复。整个 Sleep 在零模型调用、零 API key 下完成。
> 来源：Microsoft SkillOpt v0.2.0 Unreleased `--backend handoff` + Claude Code `/skillopt-sleep-handoff` 命令

---

## 48.1 总览

> **核心铁律**：Handoff Backend 让 Sleep 在零模型调用下完成——把模型决策外移到用户的 agent session，Sleep 引擎只做编排与状态机管理。每夜固定 mined tasks，确保回答 session 不能偏移任务集（保护 held-out gate 的纯洁性）。

### 三方角色

```
┌──────────────────────────────────────────────────────────────┐
│                Handoff Backend 三方角色                       │
└──────────────────────────────────────────────────────────────┘

  ① Sleep Engine（编排者）        ② PROMPTS.md（交接文件）
  ────────────────────────        ──────────────────────────
  跑 Sleep 四阶段                  每个待答模型调用写一行
  遇到模型调用 → 写 PROMPTS.md      带 pending/<id>.json schema
  exit code 3 退出                 用户 agent 读这里
       │                                │
       │    ③ User Agent Session        │
       │    ────────────────────        │
       │    用户自己的 agent 读 PROMPTS │
       │    把答案写到 answers/<id>.md  │
       │    重跑 Sleep 命令             │
       ▼                                ▼
  Sleep Engine 重跑 → 从 answers 恢复 → 继续下一阶段
```

### Handoff 循环

```
Night cycle (typically 3-6 rounds per night):

  Round 1: Engine → PROMPTS.md (exit 3) → User answers → Engine resumes
  Round 2: Engine → PROMPTS.md (exit 3) → User answers → Engine resumes
  ...
  Round N: Engine → 完成所有阶段 → best_skill 更新或拒绝
```

---

## 48.2 PROMPTS.md 与 pending.json Schema

### PROMPTS.md（人类可读交接文件）

```markdown
# SkillOpt-Sleep Handoff — Round 2 of ~5

> Engine 在等待以下模型调用的答案。请逐个回答到 `answers/<id>.md`，然后重跑：
> `skillopt-sleep --backend handoff --date 2026-07-25`

## Pending prompts

### [P1] analyst_error · stage=reflect
**Module**: skill-evolution
**Prompt**:
分析以下失败样本，提取病灶，建议 Edit。
失败样本：
- 章节第 12 段出现"他不禁想到"（L1 句式门禁触发）
- 章节第 28 段"在这个瞬间"（L2 人感禁令触发）
**Expected output format**: {patch_id, edit_op, target_module, rationale}

→ Write your answer to: `answers/P1.md`

### [P2] gate_judge · stage=gate
**Module**: meta-optimizer
**Prompt**:
比对新旧四维分数，判定 accept/reject/tie/pareto_dominated。
old: Q=0.72 S=0.85 T=0.91 R=0.68
new: Q=0.74 S=0.83 T=0.92 R=0.70
**Expected output format**: {action, rationale, pareto_check}

→ Write your answer to: `answers/P2.md`
```

### pending.json（机器可读 schema）

```json
{
  "round": 2,
  "expected_total_rounds": 5,
  "date": "2026-07-25",
  "pending": [
    {
      "id": "P1",
      "stage": "reflect",
      "module": "skill-evolution",
      "prompt_id": "analyst_error",
      "prompt_text": "...",
      "expected_format": "{patch_id, edit_op, target_module, rationale}",
      "answer_path": "answers/P1.md",
      "status": "pending"
    },
    {
      "id": "P2",
      "stage": "gate",
      "module": "meta-optimizer",
      "prompt_id": "gate_judge",
      "prompt_text": "...",
      "expected_format": "{action, rationale, pareto_check}",
      "answer_path": "answers/P2.md",
      "status": "pending"
    }
  ]
}
```

---

## 48.3 Exit Code 3 协议

> **核心铁律**：Handoff Backend 用 exit code 3 表示"等待答案"——这是与正常退出（0）、错误退出（1）的明确区分，便于脚本与 cron 调度。

| Exit Code | 含义 | 动作 |
|:----------|:-----|:-----|
| 0 | Sleep 完成 | best_skill 已更新或拒绝，无 pending |
| 1 | Sleep 错误 | 检查 error_log，重试或降级 |
| **3** | **等待答案** | 读 PROMPTS.md，写 answers，重跑同命令 |

### 状态机

```
                ┌─────────────┐
                │   START     │
                └──────┬──────┘
                       │ run --backend handoff
                       ▼
              ┌─────────────────┐
              │ Engine 跑 Sleep │
              │  遇模型调用?    │
              └────┬───────┬────┘
                   │       │
              是   │       │ 否
                   ▼       ▼
        ┌──────────┐  ┌──────────┐
        │ 写 PROMPT │  │ 完成 Sleep│
        │ exit 3   │  │ exit 0   │
        └─────┬────┘  └──────────┘
              │ user answers
              ▼
        ┌──────────┐
        │ 重跑命令  │
        │ 从答案恢复│
        └──────────┘
```

---

## 48.4 无状态恢复

> **核心铁律**：Sleep Engine 是无状态的——重跑同命令即可从 `answers/` 恢复，不需要持久化内存。Engine 重跑时先扫 `answers/`，把已答的 prompt 标 `resolved`，跳过；只对未答的继续等待。

### 恢复流程

```
Engine 启动
   │
   ▼
扫描 answers/*.md
   │
   ▼
对每个 pending[i]:
  if answers/<id>.md 存在:
    读答案
    pending[i].status = "resolved"
    pending[i].answer = <内容>
    继续跑该阶段（用答案替代模型调用）
  else:
    pending[i].status = "pending"
    保留等待
   │
   ▼
如果还有 pending:
  写新的 PROMPTS.md（只含未答的）
  exit 3
否则:
  继续下一阶段
```

### 答案校验

```
每个 answer 必须满足 expected_format：
  - JSON 格式正确
  - 必填字段齐全
  - 字段类型匹配

校验失败 → 标 "invalid"
  写回 PROMPTS.md，提示用户重答
  不进入下一阶段
```

---

## 48.5 Mined Tasks 每夜固定

> **核心铁律**：Handoff 模式下 mined tasks 在每夜开始时锁定——回答 session 不能偏移任务集。这是为了保护 held-out gate 的纯洁性：如果回答 session 能改任务集，等于训练集泄露到验证集。

### 锁定时机

```
Night start:
  Mine 阶段产出 mined_tasks.json（锁定）
       │
       ▼
Round 1..N:
  所有后续阶段都基于这个锁定的 mined_tasks.json
  回答 session 只能回答 PROMPTS.md，不能改任务集
       │
       ▼
Night end:
  mined_tasks.json 归档到 .skillopt/sleep/{date}/mined_tasks.json
  次日重新 Mine（新任务集）
```

### 锁定字段

```json
{
  "lock_ts": "2026-07-25T02:00:00Z",
  "locked_by": "handoff_backend",
  "tasks": [
    {"task_id": "T1", "session_source": "...", "pattern_id": "P_001"},
    {"task_id": "T2", "session_source": "...", "pattern_id": "P_002"}
  ],
  "lock_hash": "sha256:...",
  "modifiable": false
}
```

---

## 48.6 /skillopt-sleep-handoff 命令

### 命令定义

```bash
# 启动 handoff 循环
/skillopt-sleep-handoff

# 等价于：
#   while true:
#     skillopt-sleep --backend handoff --date {today}
#     if exit_code == 0:
#       break  # Sleep 完成
#     elif exit_code == 3:
#       # 用 fresh-context subagent 回答 PROMPTS.md
#       for prompt in pending:
#         answer = fresh_context_subagent(prompt)
#         write(answer, answers/<id>.md)
#     else:
#       break  # 错误
```

### Fresh-Context Subagent

> **核心铁律**：每个 prompt 用独立的 fresh-context subagent 回答——不让一个 subagent 同时看到多个 prompt，避免 held-out gate 的验证样本泄露到训练样本。

```
对每个 pending prompt:
  启动新的 subagent（清空上下文）
  只喂该 prompt 的内容
  收集答案
  写到 answers/<id>.md
  关闭 subagent
```

### 为什么 fresh-context 保护 held-out gate

```
❌ 错误做法（一个 subagent 答所有）：
  Subagent 看到 P1（训练样本）+ P2（验证样本）
  → P1 的内容可能影响 P2 的答案
  → 训练集泄露到验证集
  → held-out gate 失效

✅ 正确做法（fresh-context）：
  Subagent 1 只看 P1 → 答 P1
  Subagent 2 只看 P2 → 答 P2
  → 互不影响
  → held-out gate 保持纯洁
```

---

## 48.7 三种部署场景

| 场景 | 传统 Sleep | Handoff Backend |
|:-----|:-----------|:----------------|
| 有 API key + 网络 | ✅ 推荐（快） | 可用但慢 |
| 无 API key / 隐私敏感 | ❌ 不可用 | ✅ 推荐 |
| 想用本地 agent（Claude Code/Codex/Cursor） | ❌ 不可用 | ✅ 推荐 |
| 离线环境 | ❌ 不可用 | ✅ 推荐 |

### 场景示例

```
场景：用户只有本地 Claude Code，无 OpenAI API key

传统 Sleep:
  ❌ 无法跑（需要 API key 调用 optimizer/target）

Handoff Backend:
  ✅ /skillopt-sleep-handoff
  → Sleep Engine 跑到模型调用处
  → 写 PROMPTS.md
  → Claude Code fresh-context subagent 答题
  → Sleep Engine 从答案恢复
  → 3-6 轮后完成
```

---

## 48.8 与 v8.0/v10.1 的协同

### 与 v8.0 Sleep 的协同

```
v8.0 Sleep 四阶段 → 每阶段可切 backend
       │
       ▼
默认: --backend openai（需要 API key）
Handoff: --backend handoff（零 API key）
       │
       ▼
两者产出相同的 evidence.jsonl（v10.1）
```

### 与 v10.1 Evidence Chain 的协同

```
Handoff 模式下，evidence.jsonl 额外记录：
  - handoff_round: 第几轮
  - pending_prompts: 本轮待答数
  - resolved_answers: 已答数
  - fresh_context_subagents: 启动了几次 fresh subagent
  - lock_hash: mined_tasks 锁定 hash
```

---

## 48.9 安全约束

```
🚫 禁止：
  ① 一个 subagent 同时答多个 prompt（held-out 泄露）
  ② 回答 session 修改 mined_tasks（任务集偏移）
  ③ Skip 答案校验（必须满足 expected_format）
  ④ 用旧 answers 跑新夜（每夜 answers 清空）
  ⑤ Handoff 模式跳过 evidence 记录

✅ 必须：
  ① 每个 prompt 用 fresh-context subagent
  ② mined_tasks 每夜开始时锁定
  ③ Exit code 3 表示等待，0 表示完成
  ④ answers/<id>.md 满足 expected_format
  ⑤ Handoff evidence 落 evidence.jsonl
```
