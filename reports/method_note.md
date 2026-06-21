# 文献计量分析方法说明

## 项目概述
本项目对"纳米线神经突触器件"领域进行文献计量分析，数据源为 OpenAlex。

## 数据来源
- **数据源**: OpenAlex
- **时间范围**: 2020 - 2025
- **最大记录数**: 5000

## 检索策略
```
(nanowire OR nanowires) AND (synaptic OR neuromorphic OR memristor OR "artificial synapse" OR "synaptic transistor")
```

## 分析流程

### 1. 数据预处理
- 提取 OpenAlex 短 ID
- 处理缺失值
- 生成规范化表：works_clean.csv, work_references.csv, work_authors.csv, work_keywords.csv

### 2. 网络构建

| 网络类型 | 构建方法 | 说明 |
|----------|----------|------|
| 共引网络 | C = A^T @ A | 文献-参考文献矩阵的转置乘积 |
| 文献耦合 | B = A @ A^T | 文献-参考文献矩阵的乘积 |
| 关键词共现 | W = K^T @ K | 文献-关键词矩阵的转置乘积 |
| 合著网络 | M = A^T @ A | 文献-作者矩阵的转置乘积 |

### 3. 指标计算

**节点级指标**:
- degree: 节点度数
- weighted_degree: 加权度数（边权之和）
- betweenness: 介数中心性（使用 distance = 1/weight）
- pagerank: PageRank 分数
- community: 社区归属（Louvain 算法）

**图级指标**:
- n_nodes: 节点数
- n_edges: 边数
- density: 网络密度
- n_components: 连通分量数
- largest_component_ratio: 最大连通分量比例

### 4. 参数设置
- **最小边权重**: 3
- **保留 Top 边数**: 100

## 输出文件

```
outputs/
├── tables/
│   ├── co_citation_edges.csv
│   ├── coupling_edges.csv
│   ├── keyword_cooccurrence_edges.csv
│   ├── coauthorship_edges.csv
│   ├── *_node_metrics.csv
│   └── *_graph_metrics.csv
└── figures/
    ├── network_comparison.png
    └── *_analysis.png
```

## 运行命令
```bash
python -m bmmini.pipeline --config config/query.yaml --use-sample
```

---
*生成时间: 2026-06-21 20:22:39*
