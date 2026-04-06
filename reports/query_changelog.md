# 检索式变更日志 – 纳米线神经突触器件

## v0.1 (2026-03-20)

### 变更类型
- 初始版本

### 检索式结构（布尔表达式）
(
"nanowire" OR "nanowires" OR "nanowire-based" OR "nanowire array" OR "vertical nanowire" OR "core-shell nanowire"
)
AND
(
"synaptic device" OR "synaptic transistor" OR "synaptic resistor" OR "neuromorphic device" OR "neuromorphic computing" OR
"memristor" OR "memristive device" OR "artificial synapse" OR "plasticity" OR "spike-timing-dependent plasticity"
)
AND
(
"neural network" OR "brain-inspired" OR "neuromorphic hardware" OR "in-memory computing"
)

### 限定条件
| 类别 | 设定值 |
|------|--------|
| 时间窗 | 2021 – 2026 |
| 文献类型 | Article, Review |
| 语言 | English |
| 检索字段 | title, abstract, keywords |
| 数据库 | Web of Science, Scopus |

### 同义词统计
| 概念组 | 术语数量 |
|--------|----------|
| 纳米线（对象） | 9 |
| 神经突触/器件（方法） | 15 |
| 应用场景（背景） | 8 |
| **合计** | **32** |

### 设计理由
1. **三级布尔结构（对象 AND 方法 AND 场景）**：在保证查准率（precision）的同时，通过同义词扩展维持合理查全率（recall）。
2. **方法组融合多类相关器件**：包含 synaptic device、memristor、resistive switching、STDP 等，全面覆盖纳米线突触器件的不同实现路径。
3. **场景组过滤非类脑应用**：排除纯传感器、生物检测等不相关方向，提升命中文献的相关性。

### 质量验证计划
- **抽样方法**：在 Web of Science 中执行检索式，随机抽取前 50 篇文献。
- **计算指标**：人工判断相关性，计算 precision = 相关篇数/50，recall 暂估（后续与标志性论文集比对）。
- **阈值目标**：precision ≥ 0.80，recall ≥ 0.75。
- **若未达标**：
  - precision 偏低 → 增加排除词（如 NOT "sensor" NOT "cancer" NOT "biosensor"）或收紧同义词。
  - recall 偏低 → 扩展同义词（如添加 "conducting bridge", "filamentary switching", "oxide-based memristor"）或放宽时间窗。

### 后续版本规划
| 版本 | 计划内容 |
|------|----------|
| v0.2 | 根据初检结果优化同义词表，可能增加排除词 |
| v0.3 | 调整时间窗（如扩展至 2020–2026）或字段限定（加入 keyword 字段） |
| v1.0 | 定稿用于 M1 里程碑的检索式，锁定数据版本 |

---

## v0.2 (待定)
- **变更原因**：待 v0.1 验证后填写
- **具体改动**：待定
- **影响分析**：待定