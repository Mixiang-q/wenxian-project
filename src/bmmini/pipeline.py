import os
import sys
import argparse
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bmmini.normalize import process_works
from bmmini.matrices import (
    co_citation_edges,
    bibliographic_coupling_edges,
    keyword_cooccurrence_edges,
    coauthorship_edges,
    filter_top_edges
)
from bmmini.metrics import load_graph, compute_node_metrics, compute_graph_metrics


def load_config(config_path: str):
    """Load configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_normalize(config, use_sample=False):
    """Run data normalization."""
    if use_sample:
        input_path = os.path.join('data', 'raw', 'sample_works.jsonl')
    else:
        input_path = os.path.join('data', 'raw', 'openalex_works.jsonl')
    
    output_dir = config['output']['data_dir']
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        return False
    
    process_works(input_path, output_dir)
    return True


def run_matrices(config):
    """Run matrix computations."""
    data_dir = config['output']['data_dir']
    output_dir = config['output']['tables_dir']
    min_edge_weight = config['analysis'].get('min_edge_weight', 3)
    top_edges = config['analysis'].get('top_edges', 100)
    
    os.makedirs(output_dir, exist_ok=True)
    
    ref_df = pd.read_csv(os.path.join(data_dir, 'work_references.csv'))
    author_df = pd.read_csv(os.path.join(data_dir, 'work_authors.csv'))
    keyword_df = pd.read_csv(os.path.join(data_dir, 'work_keywords.csv'))
    
    edges_dict = {}
    
    co_citation = co_citation_edges(ref_df)
    co_citation = filter_top_edges(co_citation, top_n=top_edges, min_weight=min_edge_weight)
    co_citation.to_csv(os.path.join(output_dir, 'co_citation_edges.csv'), index=False)
    edges_dict['co_citation'] = co_citation
    print(f"  - Co-citation edges: {len(co_citation)}")
    
    coupling = bibliographic_coupling_edges(ref_df)
    coupling = filter_top_edges(coupling, top_n=top_edges, min_weight=min_edge_weight)
    coupling.to_csv(os.path.join(output_dir, 'coupling_edges.csv'), index=False)
    edges_dict['coupling'] = coupling
    print(f"  - Bibliographic coupling edges: {len(coupling)}")
    
    cooccurrence = keyword_cooccurrence_edges(keyword_df)
    cooccurrence = filter_top_edges(cooccurrence, top_n=top_edges, min_weight=min_edge_weight)
    cooccurrence.to_csv(os.path.join(output_dir, 'keyword_cooccurrence_edges.csv'), index=False)
    edges_dict['cooccurrence'] = cooccurrence
    print(f"  - Keyword co-occurrence edges: {len(cooccurrence)}")
    
    coauthorship = coauthorship_edges(author_df)
    coauthorship = filter_top_edges(coauthorship, top_n=top_edges, min_weight=min_edge_weight)
    coauthorship.to_csv(os.path.join(output_dir, 'coauthorship_edges.csv'), index=False)
    edges_dict['coauthorship'] = coauthorship
    print(f"  - Co-authorship edges: {len(coauthorship)}")
    
    return edges_dict


def run_metrics(config, edges_dict):
    """Run metrics computation."""
    tables_dir = config['output']['tables_dir']
    
    all_graph_metrics = []
    
    for name, edges_df in edges_dict.items():
        G = load_graph(edges_df)
        node_metrics = compute_node_metrics(G)
        graph_metrics = compute_graph_metrics(G)
        
        graph_metrics['network_type'] = name
        all_graph_metrics.append(graph_metrics)
        
        node_metrics.to_csv(os.path.join(tables_dir, f'{name}_node_metrics.csv'), index=False)
        graph_metrics_df = pd.DataFrame([graph_metrics])
        graph_metrics_df.to_csv(os.path.join(tables_dir, f'{name}_graph_metrics.csv'), index=False)
        
        print(f"  - {name}: {graph_metrics['n_nodes']} nodes, {graph_metrics['n_edges']} edges")
    
    return pd.DataFrame(all_graph_metrics)


def generate_plots(config, graph_metrics_df):
    """Generate visualization plots."""
    figures_dir = config['output']['figures_dir']
    os.makedirs(figures_dir, exist_ok=True)
    
    plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    sns.barplot(data=graph_metrics_df, x='network_type', y='n_nodes', ax=axes[0, 0])
    axes[0, 0].set_title('Number of Nodes')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    sns.barplot(data=graph_metrics_df, x='network_type', y='n_edges', ax=axes[0, 1])
    axes[0, 1].set_title('Number of Edges')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    sns.barplot(data=graph_metrics_df, x='network_type', y='density', ax=axes[1, 0])
    axes[1, 0].set_title('Network Density')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    sns.barplot(data=graph_metrics_df, x='network_type', y='largest_component_ratio', ax=axes[1, 1])
    axes[1, 1].set_title('Largest Component Ratio')
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'network_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    tables_dir = config['output']['tables_dir']
    for name in ['co_citation', 'coupling', 'cooccurrence', 'coauthorship']:
        node_metrics_path = os.path.join(tables_dir, f'{name}_node_metrics.csv')
        if os.path.exists(node_metrics_path):
            node_metrics = pd.read_csv(node_metrics_path)
            
            fig, axes = plt.subplots(1, 2, figsize=(10, 4))
            sns.histplot(node_metrics['degree'], bins=20, ax=axes[0])
            axes[0].set_title(f'{name} - Degree Distribution')
            
            top_nodes = node_metrics.nlargest(10, 'weighted_degree')
            sns.barplot(data=top_nodes, x='weighted_degree', y='node_id', ax=axes[1])
            axes[1].set_title(f'{name} - Top 10 Nodes by Weighted Degree')
            
            plt.tight_layout()
            plt.savefig(os.path.join(figures_dir, f'{name}_analysis.png'), dpi=300, bbox_inches='tight')
            plt.close()
    
    print(f"  - Plots saved to {figures_dir}")


def write_method_note(config):
    """Write method documentation."""
    reports_dir = config['output'].get('reports_dir', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    method_note = f"""# 文献计量分析方法说明

## 项目概述
本项目对"纳米线神经突触器件"领域进行文献计量分析，数据源为 OpenAlex。

## 数据来源
- **数据源**: OpenAlex
- **时间范围**: {config['query']['from_year']} - {config['query']['to_year']}
- **最大记录数**: {config['query']['max_records']}

## 检索策略
```
{config['query']['search_terms']}
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
- **最小边权重**: {config['analysis'].get('min_edge_weight', 3)}
- **保留 Top 边数**: {config['analysis'].get('top_edges', 100)}

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
*生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    with open(os.path.join(reports_dir, 'method_note.md'), 'w', encoding='utf-8') as f:
        f.write(method_note)
    
    print(f"  - Method note saved to {os.path.join(reports_dir, 'method_note.md')}")


def main():
    parser = argparse.ArgumentParser(description='Run complete literature analysis pipeline')
    parser.add_argument('--config', default='config/query.yaml', help='Path to configuration file')
    parser.add_argument('--use-sample', action='store_true', help='Use sample data instead of full data')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Literature Analysis Pipeline")
    print("=" * 60)
    
    print("\nStep 1: Loading configuration...")
    config = load_config(args.config)
    print(f"  - Configuration loaded from: {args.config}")
    
    print("\nStep 2: Normalizing data...")
    success = run_normalize(config, args.use_sample)
    if not success:
        print("  - Data normalization failed. Exiting.")
        return
    
    print("\nStep 3: Computing network edges...")
    edges_dict = run_matrices(config)
    
    print("\nStep 4: Computing network metrics...")
    graph_metrics_df = run_metrics(config, edges_dict)
    
    print("\nStep 5: Generating visualization plots...")
    generate_plots(config, graph_metrics_df)
    
    print("\nStep 6: Writing method documentation...")
    write_method_note(config)
    
    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
