import os
import sys
import argparse
import yaml
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bmmini.fetch_openalex import fetch_works
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


def run_fetch(config):
    """Run OpenAlex data fetching."""
    print("Step 1: Fetching data from OpenAlex...")
    fetch_works(config)
    print("Data fetching completed.\n")


def run_normalize(config):
    """Run data normalization."""
    print("Step 2: Normalizing data...")
    
    input_path = os.path.join('data', 'raw', 'openalex_works.jsonl')
    output_dir = config['output']['data_dir']
    
    if not os.path.exists(input_path):
        print(f"Warning: Input file not found: {input_path}")
        return
    
    process_works(input_path, output_dir)
    print("Data normalization completed.\n")


def run_matrices(config):
    """Run matrix computations."""
    print("Step 3: Computing network edges...")
    
    data_dir = config['output']['data_dir']
    output_dir = config['output']['tables_dir']
    min_edge_weight = config['analysis'].get('min_edge_weight', 3)
    top_edges = config['analysis'].get('top_edges', 100)
    
    os.makedirs(output_dir, exist_ok=True)
    
    ref_df = pd.read_csv(os.path.join(data_dir, 'work_references.csv'))
    author_df = pd.read_csv(os.path.join(data_dir, 'work_authors.csv'))
    keyword_df = pd.read_csv(os.path.join(data_dir, 'work_keywords.csv'))
    
    co_citation = co_citation_edges(ref_df)
    co_citation = filter_top_edges(co_citation, top_n=top_edges, min_weight=min_edge_weight)
    co_citation.to_csv(os.path.join(output_dir, 'co_citation_edges.csv'), index=False)
    print(f"  - Co-citation edges: {len(co_citation)}")
    
    coupling = bibliographic_coupling_edges(ref_df)
    coupling = filter_top_edges(coupling, top_n=top_edges, min_weight=min_edge_weight)
    coupling.to_csv(os.path.join(output_dir, 'coupling_edges.csv'), index=False)
    print(f"  - Bibliographic coupling edges: {len(coupling)}")
    
    cooccurrence = keyword_cooccurrence_edges(keyword_df)
    cooccurrence = filter_top_edges(cooccurrence, top_n=top_edges, min_weight=min_edge_weight)
    cooccurrence.to_csv(os.path.join(output_dir, 'keyword_cooccurrence_edges.csv'), index=False)
    print(f"  - Keyword co-occurrence edges: {len(cooccurrence)}")
    
    coauthorship = coauthorship_edges(author_df)
    coauthorship = filter_top_edges(coauthorship, top_n=top_edges, min_weight=min_edge_weight)
    coauthorship.to_csv(os.path.join(output_dir, 'coauthorship_edges.csv'), index=False)
    print(f"  - Co-authorship edges: {len(coauthorship)}")
    
    print("Network edges computation completed.\n")


def run_metrics(config):
    """Run metrics computation."""
    print("Step 4: Computing network metrics...")
    
    tables_dir = config['output']['tables_dir']
    figures_dir = config['output']['figures_dir']
    
    os.makedirs(figures_dir, exist_ok=True)
    
    edge_files = [
        'co_citation_edges.csv',
        'coupling_edges.csv',
        'keyword_cooccurrence_edges.csv',
        'coauthorship_edges.csv'
    ]
    
    for edge_file in edge_files:
        edge_path = os.path.join(tables_dir, edge_file)
        if not os.path.exists(edge_path):
            print(f"  - Skipping {edge_file}: file not found")
            continue
        
        edges_df = pd.read_csv(edge_path)
        G = load_graph(edges_df)
        
        node_metrics = compute_node_metrics(G)
        graph_metrics = compute_graph_metrics(G)
        
        base_name = os.path.splitext(edge_file)[0]
        node_metrics.to_csv(os.path.join(tables_dir, f'{base_name}_node_metrics.csv'), index=False)
        
        graph_metrics_df = pd.DataFrame([graph_metrics])
        graph_metrics_df.to_csv(os.path.join(tables_dir, f'{base_name}_graph_metrics.csv'), index=False)
        
        print(f"  - {edge_file}: {graph_metrics['n_nodes']} nodes, {graph_metrics['n_edges']} edges")
    
    print("Network metrics computation completed.\n")


def main():
    parser = argparse.ArgumentParser(description='Run the complete literature analysis pipeline')
    parser.add_argument('--config', default='config/query.yaml', help='Path to configuration file')
    parser.add_argument('--steps', default='all', help='Steps to run: fetch, normalize, matrices, metrics, or all')
    
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    steps_to_run = args.steps.split(',') if args.steps != 'all' else ['fetch', 'normalize', 'matrices', 'metrics']
    
    if 'fetch' in steps_to_run:
        run_fetch(config)
    
    if 'normalize' in steps_to_run:
        run_normalize(config)
    
    if 'matrices' in steps_to_run:
        run_matrices(config)
    
    if 'metrics' in steps_to_run:
        run_metrics(config)
    
    print("Pipeline completed successfully!")


if __name__ == '__main__':
    main()
