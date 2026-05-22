import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from bmmini.matrices import (
    co_citation_edges,
    bibliographic_coupling_edges,
    keyword_cooccurrence_edges,
    coauthorship_edges
)
from bmmini.metrics import (
    load_graph,
    compute_node_metrics,
    h_index
)


class TestMatrices:
    """Test matrix computation functions."""
    
    def test_co_citation_edges(self):
        """
        Test co-citation edge weights with small sample.
        
        Scenario:
        - Paper P1 cites Ref1, Ref2
        - Paper P2 cites Ref1, Ref2
        - Paper P3 cites Ref2, Ref3
        
        Co-citation matrix C = A^T @ A:
        - Ref1 co-cited with Ref2: 2 (P1 and P2 both cite them)
        - Ref1 co-cited with Ref3: 0
        - Ref2 co-cited with Ref3: 1 (only P3 cites both)
        """
        ref_df = pd.DataFrame([
            {'work_id': 'P1', 'reference_id': 'Ref1'},
            {'work_id': 'P1', 'reference_id': 'Ref2'},
            {'work_id': 'P2', 'reference_id': 'Ref1'},
            {'work_id': 'P2', 'reference_id': 'Ref2'},
            {'work_id': 'P3', 'reference_id': 'Ref2'},
            {'work_id': 'P3', 'reference_id': 'Ref3'}
        ])
        
        edges = co_citation_edges(ref_df, min_ref_count=1)
        
        # Find specific edges and verify weights
        ref1_ref2 = edges[(edges['source'] == 'Ref1') & (edges['target'] == 'Ref2')]
        ref2_ref3 = edges[(edges['source'] == 'Ref2') & (edges['target'] == 'Ref3')]
        
        assert len(ref1_ref2) == 1, "Ref1-Ref2 edge should exist"
        assert ref1_ref2.iloc[0]['weight'] == 2, "Ref1-Ref2 should have weight 2"
        
        assert len(ref2_ref3) == 1, "Ref2-Ref3 edge should exist"
        assert ref2_ref3.iloc[0]['weight'] == 1, "Ref2-Ref3 should have weight 1"
    
    def test_bibliographic_coupling_edges(self):
        """
        Test bibliographic coupling edge weights with small sample.
        
        Scenario:
        - Paper P1 cites Ref1, Ref2
        - Paper P2 cites Ref1, Ref2
        - Paper P3 cites Ref2, Ref3
        
        Bibliographic coupling matrix B = A @ A^T:
        - P1 coupled with P2: 2 (shared refs: Ref1, Ref2)
        - P1 coupled with P3: 1 (shared ref: Ref2)
        - P2 coupled with P3: 1 (shared ref: Ref2)
        """
        ref_df = pd.DataFrame([
            {'work_id': 'P1', 'reference_id': 'Ref1'},
            {'work_id': 'P1', 'reference_id': 'Ref2'},
            {'work_id': 'P2', 'reference_id': 'Ref1'},
            {'work_id': 'P2', 'reference_id': 'Ref2'},
            {'work_id': 'P3', 'reference_id': 'Ref2'},
            {'work_id': 'P3', 'reference_id': 'Ref3'}
        ])
        
        edges = bibliographic_coupling_edges(ref_df)
        
        p1_p2 = edges[(edges['source'] == 'P1') & (edges['target'] == 'P2')]
        p1_p3 = edges[(edges['source'] == 'P1') & (edges['target'] == 'P3')]
        p2_p3 = edges[(edges['source'] == 'P2') & (edges['target'] == 'P3')]
        
        assert len(p1_p2) == 1, "P1-P2 edge should exist"
        assert p1_p2.iloc[0]['weight'] == 2, "P1-P2 should have weight 2"
        
        assert len(p1_p3) == 1, "P1-P3 edge should exist"
        assert p1_p3.iloc[0]['weight'] == 1, "P1-P3 should have weight 1"
        
        assert len(p2_p3) == 1, "P2-P3 edge should exist"
        assert p2_p3.iloc[0]['weight'] == 1, "P2-P3 should have weight 1"


class TestMetrics:
    """Test metrics computation functions."""
    
    def test_h_index(self):
        """Test H-index computation."""
        assert h_index([10, 8, 7, 5, 4, 3, 2, 1]) == 4
        assert h_index([5, 5, 5, 5, 5]) == 5
        assert h_index([100, 20, 10, 5, 5]) == 5
        assert h_index([100, 20, 10, 5, 1]) == 4
        assert h_index([]) == 0
        assert h_index([0]) == 0
        assert h_index([1]) == 1
    
    def test_node_metrics_contains_betweenness(self):
        """Test that node metrics output contains betweenness column."""
        edges_df = pd.DataFrame([
            {'source': 'A', 'target': 'B', 'weight': 1},
            {'source': 'B', 'target': 'C', 'weight': 1},
            {'source': 'A', 'target': 'C', 'weight': 1}
        ])
        
        G = load_graph(edges_df)
        node_metrics = compute_node_metrics(G)
        
        assert 'betweenness' in node_metrics.columns, "betweenness column should exist"
        assert 'degree' in node_metrics.columns, "degree column should exist"
        assert 'weighted_degree' in node_metrics.columns, "weighted_degree column should exist"
        assert 'pagerank' in node_metrics.columns, "pagerank column should exist"
        assert 'community' in node_metrics.columns, "community column should exist"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
