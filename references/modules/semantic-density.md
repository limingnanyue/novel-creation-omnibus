# 第53章：语义密度验证门（Semantic Density Gate）

> 适用："语义密度" "semantic density" "信息密度门" "density gate" "novelty per token" "信息熵验证" "稀薄文本检测" "水分检测" "density_score"
> 核心理念：v7.0 验证门只看"分数通过"——但通过分数的输出可能是"水"：重复、空泛、堆砌形容词、信息量稀薄。v10.7 引入语义密度验证门——用每 token 信息熵+实体密度+论点密度三个指标，识别"看似 OK 实则空心"的输出，避免 best_skill 被稀薄 rollout 污染。
> 来源：Microsoft SkillOpt v0.2.0 `skillopt/gate/semantic_density.py` + `skillopt/prompts/semantic_density.md`

---

## 53.1 总览

> **核心铁律**：一个 rollout 即使分数达标，若语义密度低于阈值——它就是"水"——不该被 accept 进入 best_skill。语义密度 = 单位 token 携带的"可索引信息量"。

### v7.0 分数门 vs v10.7 密度门

| 维度 | v7.0 分数门 | v10.7 语义密度门 |
|:-----|:-----------|:-----------------|
| 通过判据 | 五维分数 D1-D5 ≥ 阈值 | 分数达标 AND 密度达标 |
| 检测盲区 | 重复/堆砌/水文本可拿高分 | 显式检测"水" |
| 指标 | 5 维分数 | 3 维密度（信息熵+实体+论点） |
| 失败原因 | "不够好" | "水分多/信息稀薄/论点空心" |
| 反馈给反思 | 模糊 | 精确指出哪段水 |

### 三维密度指标

```
semantic_density = w1 × info_entropy + w2 × entity_density + w3 × claim_density

  info_entropy:   每 token 信息熵（去除重复/模板/套话后的熵）
  entity_density: 每 100 token 的命名实体数（人/地/物/事件）
  claim_density:  每 100 token 的论点数（动作/转折/因果）

默认权重: w1=0.4, w2=0.3, w3=0.3
密度阈值: density_threshold = 0.5（<0.5 视为稀薄）
```

---

## 53.2 三维密度指标详解

### ① info_entropy（信息熵）

```
计算流程:
  1. 文本切片为 token 序列
  2. 去除模板/套话/重复 n-gram（用 v6.1 去AI味词表）
  3. 计算剩余 token 的 Shannon 熵:
     H = -Σ p(t) × log2(p(t))
  4. 归一化: info_entropy = H / H_max（H_max 为完全均匀分布的熵）

例:
  原文: "他仿佛感受到了内心的触动，仿佛整个世界都变了，仿佛一切都不一样了。"
  去重后: "他仿佛感受到了内心的触动，整个世界都变了，一切都不一样了。"
  → 重复"仿佛"导致熵降低，info_entropy ≈ 0.42（稀薄）

  原文: "他推开窗，街角那盏路灯正亮着，雨刚停，屋檐还在滴水。"
  → 实体丰富，句式多样，info_entropy ≈ 0.78（密实）
```

### ② entity_density（实体密度）

```
计算流程:
  1. 抽取命名实体（NER）：人/地/物/事件/时间/动作主体
  2. entity_density = entity_count / (token_count / 100)

例:
  "他感到温暖，心中涌起一股感觉" → 0 实体 / 14 token → density = 0（空心）
  "林深推开门，看到苏晚站在门口，手里拿着那把红伞" → 3 实体 / 22 token → density ≈ 13.6（密实）

阈值:
  entity_density < 2.0 → 空心（扣分）
  entity_density ≥ 5.0 → 密实（加分）
```

### ③ claim_density（论点密度）

```
计算流程:
  1. 抽取"论点"：动作/转折/因果/决策/状态变化
  2. claim_density = claim_count / (token_count / 100)

例:
  "他觉得很好，他觉得很有意思，他觉得有点意思" → 0 论点 / 19 token → density = 0（水）
  "他拒绝了她，转身离开，走出三步又停下，回头说了一句话" → 4 论点 / 24 token → density ≈ 16.7（密实）

阈值:
  claim_density < 3.0 → 空心（扣分）
  claim_density ≥ 6.0 → 密实（加分）
```

---

## 53.3 密度门验证流程

```
v7.0 验证门通过后 → 触发 v10.7 密度门:

  density_score = 0.4 × info_entropy + 0.3 × entity_density_norm + 0.3 × claim_density_norm

  if density_score ≥ 0.7:
    → ACCEPT（密实，进 best_skill）
  elif 0.5 ≤ density_score < 0.7:
    → ACCEPT_WITH_WARNING（边缘，标记稀薄段落，进 best_skill 但加 watermark）
  elif 0.3 ≤ density_score < 0.5:
    → REJECT_DILUTE（稀薄，退回反思产 Edit 解决水）
  else:
    → REJECT_HOLLOW（空心，直接拒绝，进 rejected_edits 缓冲）
```

### 三态拒绝动作

```
REJECT_DILUTE:
  - 标记稀薄段落
  - 触发 v10.6 技能感知反思
  - Edit 落点: 对应模块的"密度要求"段
  - 例: "anti-ai-polish#§3.5-水分检测-补丁"

REJECT_HOLLOW:
  - 直接拒绝，不进 best_skill
  - 进 rejected_edits.jsonl 缓冲（v7.0 拒绝编辑缓冲三态迁移）
  - 频次≥3 → 升级为通用 Edit（"该模块普遍产出空心文本"）
```

---

## 53.4 与 v7.0/v10.6 的协同

### 与 v7.0 验证门的协同

```
v7.0 验证门（五维分数 D1-D5）:
  ↓ 通过

v10.7 密度门（三维密度）:
  ↓ 通过 → ACCEPT
  ↓ 边缘 → ACCEPT_WITH_WARNING
  ↓ 稀薄 → REJECT_DILUTE（触发反思）
  ↓ 空心 → REJECT_HOLLOW（直接拒绝）

两门串联不替代:
  v7.0 看"质量是否达标"
  v10.7 看"达标后是否密实"
  两门都过才进 best_skill
```

### 与 v10.6 技能感知反思的协同

```
REJECT_DILUTE 触发的反思:
  用 v10.6 技能感知反思模板
  failure_signal = "语义密度低: info_entropy=0.42, entity_density=1.8, claim_density=2.5"
  skill_anchor 定位到模块的"密度要求"段
  产段落级 Edit: 增加密度约束/反例/检查项
```

---

## 53.5 密度日志与审计

### semantic_density_log.jsonl

```json
{
  "rollout_id": "rollout_42",
  "module": "core-writing",
  "token_count": 2340,
  "density_scores": {
    "info_entropy": 0.78,
    "entity_density": 6.2,
    "claim_density": 7.1,
    "composite": 0.81
  },
  "sparse_segments": [
    {
      "start": 120,
      "end": 180,
      "text": "他仿佛感受到了内心的触动...",
      "reason": "重复'仿佛'+无实体+无论点"
    }
  ],
  "gate_decision": "ACCEPT_WITH_WARNING",
  "watermark": "density_warning_v10.7",
  "ts": "2026-07-25T03:00:00Z"
}
```

### 审计指标

```
密度门健康度:
  - density_pass_rate: 密度门通过率（目标 ≥ 0.7）
  - dilute_reject_rate: 稀薄拒绝率（目标 0.05-0.15，过高=产出质量下滑）
  - hollow_reject_rate: 空心拒绝率（目标 < 0.05，过高=严重退化）
  - sparse_segment_count: 平均每 rollout 稀薄段数（目标 ≤ 1）

异常:
  - dilute_reject_rate > 0.3 → 产出普遍稀薄，触发 v9.0 元反思五问
  - hollow_reject_rate > 0.1 → best_skill 已被污染，触发回滚
```

---

## 53.6 配置

```yaml
# .skillopt/semantic-density.yaml
semantic_density:
  enabled: true
  weights:
    info_entropy: 0.4
    entity_density: 0.3
    claim_density: 0.3
  thresholds:
    accept: 0.7
    accept_with_warning: 0.5
    reject_dilute: 0.3
    # < 0.3 → reject_hollow
  entity_density:
    sparse_below: 2.0
    dense_above: 5.0
  claim_density:
    sparse_below: 3.0
    dense_above: 6.0
  sparse_segment_detection: true
  trigger_reflect_on_dilute: true  # REJECT_DILUTE 触发 v10.6 反思
```

---

## 53.7 触发词与路由

### 触发词

```
- 语义密度
- semantic density
- 信息密度门
- density gate
- novelty per token
- 信息熵验证
- 稀薄文本检测
- 水分检测
- density_score
- 空心文本
- 论点密度
- 实体密度
```

### 路由规则

| 用户说 | 动作 |
|:-------|:-----|
| "查语义密度" / "density check" | 跑密度门，输出三维分数+稀薄段 |
| "看稀薄段" / "sparse segments" | 列出最近 N rollout 的稀薄段 |
| "密度审计" / "density audit" | 输出密度门健康度 4 项指标 |
| "调密度阈值" | 修改 thresholds 配置 |

---

## 53.8 安全约束

```
🚫 禁止：
  ① 跳过 v7.0 分数门直接跑密度门（密度门是串联不是并联）
  ② 密度门拒绝后不触发反思（REJECT_DILUTE 必须触发 v10.6）
  ③ 密度阈值动态修改（避免攻击者降阈值通过水文本）
  ④ 不记录稀薄段位置（必须落 sparse_segments）
  ⑤ 把 REJECT_HOLLOW 当 REJECT_DILUTE 处理（空心直接拒绝不反思）

✅ 必须：
  ① 三维指标都要算（不能只算一个）
  ② 稀薄段必须定位+标记
  ③ 密度日志只追加不修改
  ④ 审计指标每天输出
  ⑤ watermark 标记的 ACCEPT_WITH_WARNING 进 best_skill 但可追溯
```
