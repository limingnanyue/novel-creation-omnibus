# 第50章：LLM Miner 大模型矿工

> 适用："LLM 矿工" "llm miner" "智能模式挖掘" "模式抽象" "模式泛化" "频次+置信度双门" "语义聚类" " Sleep 矿工升级" "替代纯频次"
> 核心理念：v8.0 Sleep Mine 阶段用纯频次过滤（频次≥3 进 Replay），但相同模式可能以不同表面形式出现，纯频次会漏掉语义相同但表述不同的模式。v10.4 引入 LLM Miner——用 LLM 做语义聚类+抽象+泛化，让"看似不同的失败"被识别为"同一类病灶"。频次+LLM 置信度双门过滤。
> 来源：Microsoft SkillOpt v0.2.0 `skillopt_sleep/llm_miner.py`

---

## 50.1 总览

> **核心铁律**：纯频次会漏掉语义相同但表述不同的模式。LLM Miner 用 LLM 做：① 语义聚类（把表面不同的归一类）② 抽象（提取模式骨架）③ 泛化（识别适用范围）。最终用 频次≥3 AND LLM 置信度≥0.7 双门过滤进 Replay。

### v8.0 vs v10.4 Mine 对比

| 维度 | v8.0 Mine（纯频次） | v10.4 LLM Miner |
|:-----|:-------------------|:----------------|
| 过滤 | 频次≥3 | 频次≥3 **AND** LLM 置信度≥0.7 |
| 聚类 | 表面字符串匹配 | 语义聚类（LLM 判定同义） |
| 抽象 | 无（保留原始表述） | 提取模式骨架 |
| 泛化 | 无 | 识别适用范围 |
| 漏检 | 高（语义同表述不同 → 漏） | 低 |
| 误检 | 中（高频但无意义 → 误） | 低（LLM 置信度过滤） |

### LLM Miner 四步

```
┌─────────────────────────────────────────────────────┐
│                LLM Miner 四步流程                     │
└─────────────────────────────────────────────────────┘

  ① Extract（提取）
  ─────────────
  从 harvested sessions 提取所有候选模式
  候选 = 失败片段 + 上下文 + 失败原因

  ② Cluster（语义聚类）
  ────────────────────
  LLM 判定哪些候选语义相同
  聚类: C1={c1,c2,c3...}, C2={c4,c5...}, ...

  ③ Abstract（抽象）
  ────────────────
  对每个聚类，LLM 提取模式骨架
  "在第X章用了'他不禁想到'，第Y章用了'他暗自思忖'"
  → 抽象: "内心独白用 AI 高频词"

  ④ Generalize（泛化）
  ─────────────────
  LLM 识别模式适用范围
  "内心独白用 AI 高频词" → 适用: 所有内心独白场景

  双门过滤:
    频次(聚类大小) ≥ 3
    AND
    LLM 置信度 ≥ 0.7
    → 进 Replay
```

---

## 50.2 语义聚类

> **核心铁律**：纯字符串匹配会把"他不禁想到"和"他暗自思忖"当作两个不同模式，但它们语义相同（都是 AI 高频内心独白词）。LLM 聚类把它们归为一类。

### 聚类 prompt 示例

```
你是模式聚类器。判定以下候选模式哪些语义相同（同一类病灶的不同表述）。

候选:
  c1: "第12段用了'他不禁想到'" (失败: L1句式门禁)
  c2: "第28段用了'他暗自思忖'" (失败: L1句式门禁)
  c3: "第45段用了'在这个瞬间他意识到'" (失败: L2人感禁令)
  c4: "第8段对话占比<30%" (失败: 节奏问题)
  c5: "第33段用了'他不禁想到'" (失败: L1句式门禁)

输出 JSON:
{
  "clusters": [
    {
      "cluster_id": "C1",
      "members": ["c1", "c2", "c3", "c5"],
      "semantic_label": "内心独白用 AI 高频词",
      "confidence": 0.92
    },
    {
      "cluster_id": "C2",
      "members": ["c4"],
      "semantic_label": "对话占比不足",
      "confidence": 0.85
    }
  ]
}
```

### 聚类规则

```
① 同一 cluster 的成员必须语义相同（同一类病灶）
② 不同 cluster 的成员必须语义不同
③ 单成员 cluster 允许（频次=1，但 LLM 置信度高时仍可进 Replay）
④ confidence ≥ 0.7 才视为有效聚类
```

---

## 50.3 抽象与泛化

### 抽象（Abstract）

> 提取模式骨架，去掉具体章节/段落数，保留通用特征。

```
聚类 C1 成员:
  c1: "第12段用了'他不禁想到'"
  c2: "第28段用了'他暗自思忖'"
  c3: "第45段用了'在这个瞬间他意识到'"
  c5: "第33段用了'他不禁想到'"

抽象后:
  pattern_skeleton: "内心独白场景使用 AI 高频词"
  instances: ["他不禁想到", "他暗自思忖", "在这个瞬间他意识到"]
  abstract_confidence: 0.92
```

### 泛化（Generalize）

> 识别模式适用范围，让 Edit 能覆盖更多场景。

```
抽象: "内心独白场景使用 AI 高频词"

泛化:
  applicable_scenes:
    - 内心独白
    - 心理描写
    - 回忆插入
  applicable_modules:
    - anti-ai-polish.md (L1 句式门禁)
    - dialogue-mastery.md (声线档案)
  generalize_confidence: 0.88
```

---

## 50.4 双门过滤

> **核心铁律**：进 Replay 必须同时满足频次≥3 AND LLM 置信度≥0.7。单门通过不足以进 Replay。

### 过滤矩阵

| 频次 | LLM 置信度 | 决策 |
|:-----|:-----------|:-----|
| ≥3 | ≥0.7 | ✅ 进 Replay |
| ≥3 | <0.7 | ⚠️ 标"低置信高频"，进观察池（不进 Replay） |
| <3 | ≥0.7 | ⚠️ 标"高置信低频"，进观察池（可能新兴模式） |
| <3 | <0.7 | ❌ 丢弃（偶发噪声） |

### 观察池机制

```
观察池 patterns_staging.jsonl:
  - 低置信高频: 频次高但 LLM 不确定，等下夜 LLM 重判
  - 高置信低频: LLM 确信但频次低，等下夜频次累积

连续 3 夜仍在观察池 → 升级进 Replay（足够证据）
连续 7 夜仍在观察池 → 降级丢弃（无累积证据）
```

---

## 50.5 LLM Miner Schema

### Pattern Schema

```json
{
  "pattern_id": "P_LLM_001",
  "miner": "llm_miner",
  "mine_date": "2026-07-25",
  "cluster_members": ["c1", "c2", "c3", "c5"],
  "cluster_size": 4,
  "semantic_label": "内心独白用 AI 高频词",
  "pattern_skeleton": "内心独白场景使用 AI 高频词",
  "instances": ["他不禁想到", "他暗自思忖", "在这个瞬间他意识到"],
  "applicable_scenes": ["内心独白", "心理描写", "回忆插入"],
  "applicable_modules": ["anti-ai-polish.md", "dialogue-mastery.md"],
  "freq": 4,
  "llm_confidence": 0.92,
  "abstract_confidence": 0.92,
  "generalize_confidence": 0.88,
  "composite_confidence": 0.91,
  "filter_decision": "replay",
  "filter_reason": "freq≥3 AND llm_confidence≥0.7"
}
```

### Miner Output Schema

```json
{
  "mine_date": "2026-07-25",
  "total_candidates": 47,
  "total_clusters": 12,
  "valid_clusters": 8,
  "replay_patterns": 5,
  "staging_patterns": 2,
  "dropped_patterns": 5,
  "patterns": [...]
}
```

---

## 50.6 与 v8.0/v10.3 的协同

### 与 v8.0 Sleep Mine 的协同

```
v8.0 Mine（纯频次）→ 候选模式池
       │
       ▼
v10.4 LLM Miner → 语义聚类+抽象+泛化+双门过滤
       │
       ▼
进 Replay 的模式（更精准）
```

### 与 v10.3 Contrastive Reflection 的协同

```
v10.4 LLM Miner 产出 pattern_skeleton
       │
       ▼
v10.3 Contrastive Reflect 用 pattern_skeleton 做差异提取
（不再用原始字符串，用抽象后的骨架）
       │
       ▼
通用 Edit 的 scope 更精准
```

---

## 50.7 触发词与路由

### 触发词

```
- LLM 矿工
- llm miner
- 智能模式挖掘
- 模式抽象
- 模式泛化
- 频次+置信度双门
- 语义聚类
- Sleep 矿工升级
- 替代纯频次
- 模式骨架
- 观察池
```

### 路由规则

| 用户说 | 动作 |
|:-------|:-----|
| "LLM 矿工" / "llm miner" | 跑 LLM Miner 四步，输出聚类+抽象+泛化+双门过滤结果 |
| "查看观察池" / "staging patterns" | 输出当前观察池状态 |
| "模式抽象" / "pattern abstract" | 对指定聚类做抽象 |

---

## 50.8 安全约束

```
🚫 禁止：
  ① 跳过双门过滤（频次 OR 置信度单门通过就进 Replay）
  ② LLM 置信度 < 0.5 的聚类直接进 Replay
  ③ 单成员聚类不经观察池直接进 Replay
  ④ 抽象后的 pattern_skeleton 丢失关键特征

✅ 必须：
  ① 频次≥3 AND LLM 置信度≥0.7 双门
  ② 观察池连续 3 夜才升级
  ③ 抽象保留 instances 列表（可追溯）
  ④ 泛化标 applicable_scenes + applicable_modules
```
