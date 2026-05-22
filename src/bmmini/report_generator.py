#!/usr/bin/env python3
"""
报告生成器：根据网络分析结果生成解读报告
"""

import argparse
import os
import pandas as pd
import yaml
from datetime import datetime


def load_graph_metrics(filepath):
    """加载图级指标"""
    try:
        df = pd.read_csv(filepath)
        return df.iloc[0].to_dict()
    except FileNotFoundError:
        return {}


def load_node_metrics(filepath, top_n=3):
    """加载节点指标并获取Top节点"""
    try:
        df = pd.read_csv(filepath)
        df = df.sort_values('weighted_degree', ascending=False).head(top_n)
        return df['node_id'].tolist()
    except FileNotFoundError:
        return []


def get_bridge_node(filepath):
    """获取介数中心性最高的节点"""
    try:
        df = pd.read_csv(filepath)
        return df.sort_values('betweenness', ascending=False).iloc[0]['node_id']
    except (FileNotFoundError, KeyError, IndexError):
        return None


def generate_report(input_dir, output_path, config_path):
    """生成结果解读报告"""
    # 加载配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 加载各类网络指标
    networks = {
        'keyword_cooccurrence': '关键词共现网络',
        'co_citation': '共引网络',
        'coupling': '文献耦合网络',
        'coauthorship': '合著网络'
    }
    
    metrics = {}
    top_nodes = {}
    bridge_nodes = {}
    
    for net_name in networks.keys():
        graph_metrics = load_graph_metrics(
            os.path.join(input_dir, f'{net_name}_edges_graph_metrics.csv')
        )
        node_metrics_path = os.path.join(input_dir, f'{net_name}_edges_node_metrics.csv')
        
        metrics[net_name] = graph_metrics
        top_nodes[net_name] = load_node_metrics(node_metrics_path)
        bridge_nodes[net_name] = get_bridge_node(node_metrics_path)
    
    # 读取模板
    template_path = os.path.join(os.path.dirname(output_path), 'result_interpretation_template.md')
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 准备填充数据
    query_config = config.get('query', {})
    analysis_config = config.get('analysis', {})
    
    def get_density_desc(density):
        if density < 0.01:
            return '稀疏'
        elif density < 0.1:
            return '较为稀疏'
        elif density < 0.3:
            return '适中'
        else:
            return '较为密集'
    
    def get_lcc_desc(lcc_ratio):
        if lcc_ratio > 0.8:
            return '整体连通性较好'
        elif lcc_ratio > 0.5:
            return '存在较大连通分量'
        else:
            return '连通性较差'
    
    def get_component_desc(n_components, n_nodes):
        if n_components < n_nodes * 0.1:
            return '整体连通性较好'
        elif n_components < n_nodes * 0.3:
            return '存在多个研究社区'
        else:
            return '较为分散'
    
    def get_communities(node_metrics_path):
        """获取社区数量"""
        try:
            df = pd.read_csv(node_metrics_path)
            return len(df['community'].unique())
        except FileNotFoundError:
            return 'N/A'
    
    fill_data = {
        'keyword_cooccurrence_nodes': metrics['keyword_cooccurrence'].get('n_nodes', 0),
        'keyword_cooccurrence_edges': metrics['keyword_cooccurrence'].get('n_edges', 0),
        'keyword_cooccurrence_density': metrics['keyword_cooccurrence'].get('density', 0),
        'keyword_cooccurrence_density_desc': get_density_desc(metrics['keyword_cooccurrence'].get('density', 0)),
        'keyword_top3': ', '.join([f'`{n}`' for n in top_nodes['keyword_cooccurrence']]),
        'keyword_bridge_node': bridge_nodes['keyword_cooccurrence'] or 'N/A',
        
        'co_citation_nodes': metrics['co_citation'].get('n_nodes', 0),
        'co_citation_edges': metrics['co_citation'].get('n_edges', 0),
        'co_citation_lcc_ratio': metrics['co_citation'].get('largest_component_ratio', 0),
        'co_citation_lcc_desc': get_lcc_desc(metrics['co_citation'].get('largest_component_ratio', 0)),
        'citation_top3': ', '.join([f'`{n}`' for n in top_nodes['co_citation']]),
        'citation_pivot_node': bridge_nodes['co_citation'] or 'N/A',
        
        'coupling_nodes': metrics['coupling'].get('n_nodes', 0),
        'coupling_edges': metrics['coupling'].get('n_edges', 0),
        'coupling_density': metrics['coupling'].get('density', 0),
        'coupling_density_desc': get_density_desc(metrics['coupling'].get('density', 0)),
        'coupling_cluster_center': bridge_nodes['coupling'] or 'N/A',
        'coupling_communities': get_communities(os.path.join(input_dir, 'coupling_edges_node_metrics.csv')),
        
        'coauthorship_nodes': metrics['coauthorship'].get('n_nodes', 0),
        'coauthorship_edges': metrics['coauthorship'].get('n_edges', 0),
        'coauthorship_components': metrics['coauthorship'].get('n_components', 0),
        'coauthorship_components_desc': get_component_desc(metrics['coauthorship'].get('n_components', 0), metrics['coauthorship'].get('n_nodes', 1)),
        'author_top3': ', '.join([f'`{n}`' for n in top_nodes['coauthorship']]),
        'author_hub': bridge_nodes['coauthorship'] or 'N/A',
        'coauthorship_communities': get_communities(os.path.join(input_dir, 'coauthorship_edges_node_metrics.csv')),
        
        'min_edge_weight': analysis_config.get('min_edge_weight', 3),
        'min_ref_count': analysis_config.get('min_edge_weight', 3),
        'min_pubs': analysis_config.get('min_edge_weight', 3),
        'from_year': query_config.get('from_year', 2020),
        'to_year': query_config.get('to_year', 2025),
        'max_records': query_config.get('max_records', 5000),
        'report_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 填充模板
    report = template.format(**fill_data)
    
    # 保存报告
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已生成: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='生成文献计量分析结果解读报告')
    parser.add_argument('--input', default='outputs/tables', help='网络指标表格目录')
    parser.add_argument('--output', default='reports/result_interpretation.md', help='输出报告路径')
    parser.add_argument('--config', default='config/query.yaml', help='配置文件路径')
    args = parser.parse_args()
    
    generate_report(args.input, args.output, args.config)


if __name__ == '__main__':
    main()
