"""bmmini - Bibliometric Analysis Module"""
__version__ = "0.1.0"

from .fetch_openalex import fetch_works
from .normalize import process_works
from .matrices import (
    co_citation_edges,
    bibliographic_coupling_edges,
    keyword_cooccurrence_edges,
    coauthorship_edges,
    filter_top_edges
)
from .metrics import load_graph, compute_node_metrics, compute_graph_metrics
from .pipeline import main as run_pipeline

__all__ = [
    'fetch_works',
    'process_works',
    'co_citation_edges',
    'bibliographic_coupling_edges',
    'keyword_cooccurrence_edges',
    'coauthorship_edges',
    'filter_top_edges',
    'load_graph',
    'compute_node_metrics',
    'compute_graph_metrics',
    'run_pipeline'
]
