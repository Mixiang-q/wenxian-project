import pandas as pd
import numpy as np
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
from typing import Dict, Tuple


def load_graph(edges_df: pd.DataFrame) -> nx.Graph:
    """
    Load graph from edges DataFrame.
    
    Args:
        edges_df: DataFrame with source, target, weight
    
    Returns:
        NetworkX Graph with distance attribute (1/weight)
    """
    G = nx.Graph()
    
    for _, row in edges_df.iterrows():
        G.add_edge(
            row['source'],
            row['target'],
            weight=row['weight'],
            distance=1.0 / row['weight']
        )
    
    return G


def compute_node_metrics(G: nx.Graph) -> pd.DataFrame:
    """
    Compute node-level metrics.
    
    Args:
        G: NetworkX Graph
    
    Returns:
        DataFrame with node_id, degree, weighted_degree, betweenness, pagerank, community
    """
    metrics = []
    
    degree = dict(G.degree())
    weighted_degree = dict(G.degree(weight='weight'))
    
    betweenness = nx.betweenness_centrality(G, weight='distance', normalized=True)
    
    pagerank = nx.pagerank(G, weight='weight')
    
    communities = greedy_modularity_communities(G, weight='weight')
    partition = {}
    for comm_id, comm in enumerate(communities):
        for node in comm:
            partition[node] = comm_id
    
    for node in G.nodes():
        metrics.append({
            'node_id': node,
            'degree': degree[node],
            'weighted_degree': weighted_degree[node],
            'betweenness': betweenness[node],
            'pagerank': pagerank[node],
            'community': partition[node]
        })
    
    return pd.DataFrame(metrics)


def h_index(citations: list) -> int:
    """
    Compute H-index from a list of citation counts.
    
    Args:
        citations: List of citation counts (sorted or unsorted)
    
    Returns:
        H-index value
    """
    if not citations:
        return 0
    
    sorted_citations = sorted(citations, reverse=True)
    h = 0
    for i, cites in enumerate(sorted_citations, 1):
        if cites >= i:
            h = i
        else:
            break
    return h


def compute_graph_metrics(G: nx.Graph) -> Dict[str, float]:
    """
    Compute graph-level metrics.
    
    Args:
        G: NetworkX Graph
    
    Returns:
        Dictionary with n_nodes, n_edges, density, n_components, largest_component_ratio
    """
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    
    if n_nodes > 1:
        density = nx.density(G)
    else:
        density = 0.0
    
    components = list(nx.connected_components(G))
    n_components = len(components)
    
    if components:
        largest_size = max(len(c) for c in components)
        largest_component_ratio = largest_size / n_nodes
    else:
        largest_component_ratio = 0.0
    
    return {
        'n_nodes': n_nodes,
        'n_edges': n_edges,
        'density': density,
        'n_components': n_components,
        'largest_component_ratio': largest_component_ratio
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Compute network metrics')
    parser.add_argument('--input', required=True, help='Path to edges CSV')
    parser.add_argument('--output', required=True, help='Output directory')
    
    args = parser.parse_args()
    
    edges_df = pd.read_csv(args.input)
    G = load_graph(edges_df)
    
    node_metrics_df = compute_node_metrics(G)
    graph_metrics = compute_graph_metrics(G)
    
    node_metrics_df.to_csv(f'{args.output}/node_metrics.csv', index=False)
    
    graph_metrics_df = pd.DataFrame([graph_metrics])
    graph_metrics_df.to_csv(f'{args.output}/graph_metrics.csv', index=False)
    
    print(f"Node metrics saved to: {args.output}/node_metrics.csv")
    print(f"Graph metrics saved to: {args.output}/graph_metrics.csv")
    print(f"Graph metrics: {graph_metrics}")


if __name__ == '__main__':
    main()
