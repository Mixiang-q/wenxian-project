import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
import time


def build_incidence_matrix(edge_df: pd.DataFrame, row_col: str, col_col: str, min_count: int = 2) -> tuple:
    """
    Build incidence matrix from edge dataframe with optional filtering.
    
    Args:
        edge_df: DataFrame with edges
        row_col: Column name for rows
        col_col: Column name for columns
        min_count: Minimum occurrences to include column items
    
    Returns:
        (csr_matrix, row_index, col_index)
    """
    if min_count > 1:
        col_counts = edge_df[col_col].value_counts()
        valid_cols = col_counts[col_counts >= min_count].index
        edge_df = edge_df[edge_df[col_col].isin(valid_cols)]
    
    row_unique = edge_df[row_col].unique()
    col_unique = edge_df[col_col].unique()
    
    row_index = {v: i for i, v in enumerate(row_unique)}
    col_index = {v: i for i, v in enumerate(col_unique)}
    
    rows = edge_df[row_col].map(row_index).values
    cols = edge_df[col_col].map(col_index).values
    data = np.ones(len(edge_df))
    
    matrix = csr_matrix((data, (rows, cols)), shape=(len(row_unique), len(col_unique)))
    
    return matrix, row_index, col_index


def co_citation_edges(ref_df: pd.DataFrame, min_ref_count: int = 3) -> pd.DataFrame:
    """
    Compute co-citation edges.
    
    Args:
        ref_df: DataFrame with work_id and reference_id
        min_ref_count: Minimum citations for a reference to be included
    
    Returns:
        DataFrame with source, target, weight
    """
    print(f"  Building co-citation matrix...")
    start = time.time()
    
    matrix, work_index, ref_index = build_incidence_matrix(ref_df, 'work_id', 'reference_id', min_ref_count)
    print(f"    Matrix shape: {matrix.shape}")
    
    co_citation_matrix = matrix.T @ matrix
    print(f"    Matrix multiplication done in {time.time() - start:.2f}s")
    
    edges = _matrix_to_edges(co_citation_matrix, ref_index)
    print(f"    Generated {len(edges)} co-citation edges")
    
    return edges


def bibliographic_coupling_edges(ref_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute bibliographic coupling edges.
    
    Args:
        ref_df: DataFrame with work_id and reference_id
    
    Returns:
        DataFrame with source, target, weight
    """
    print(f"  Building bibliographic coupling matrix...")
    start = time.time()
    
    matrix, work_index, ref_index = build_incidence_matrix(ref_df, 'work_id', 'reference_id')
    print(f"    Matrix shape: {matrix.shape}")
    
    coupling_matrix = matrix @ matrix.T
    print(f"    Matrix multiplication done in {time.time() - start:.2f}s")
    
    edges = _matrix_to_edges(coupling_matrix, work_index)
    print(f"    Generated {len(edges)} coupling edges")
    
    return edges


def keyword_cooccurrence_edges(keyword_df: pd.DataFrame, min_kw_count: int = 3) -> pd.DataFrame:
    """
    Compute keyword co-occurrence edges.
    
    Args:
        keyword_df: DataFrame with work_id and keyword
        min_kw_count: Minimum occurrences for a keyword to be included
    
    Returns:
        DataFrame with source, target, weight
    """
    print(f"  Building keyword co-occurrence matrix...")
    start = time.time()
    
    matrix, work_index, keyword_index = build_incidence_matrix(keyword_df, 'work_id', 'keyword', min_kw_count)
    print(f"    Matrix shape: {matrix.shape}")
    
    cooccurrence_matrix = matrix.T @ matrix
    print(f"    Matrix multiplication done in {time.time() - start:.2f}s")
    
    edges = _matrix_to_edges(cooccurrence_matrix, keyword_index)
    print(f"    Generated {len(edges)} keyword co-occurrence edges")
    
    return edges


def coauthorship_edges(author_df: pd.DataFrame, min_pubs: int = 2) -> pd.DataFrame:
    """
    Compute co-authorship edges.
    
    Args:
        author_df: DataFrame with work_id and author_id
        min_pubs: Minimum publications for an author to be included
    
    Returns:
        DataFrame with source, target, weight
    """
    print(f"  Building co-authorship matrix...")
    start = time.time()
    
    if min_pubs > 1:
        author_counts = author_df['author_id'].value_counts()
        valid_authors = author_counts[author_counts >= min_pubs].index
        author_df = author_df[author_df['author_id'].isin(valid_authors)]
    
    matrix, work_index, author_index = build_incidence_matrix(author_df, 'work_id', 'author_id')
    print(f"    Matrix shape: {matrix.shape}")
    
    coauthorship_matrix = matrix.T @ matrix
    print(f"    Matrix multiplication done in {time.time() - start:.2f}s")
    
    edges = _matrix_to_edges(coauthorship_matrix, author_index)
    print(f"    Generated {len(edges)} co-authorship edges")
    
    return edges


def _matrix_to_edges(matrix: csr_matrix, index_map: dict) -> pd.DataFrame:
    """
    Convert sparse matrix to edge list with source, target, weight.
    
    Args:
        matrix: Sparse matrix
        index_map: Mapping from index to original ID
    
    Returns:
        DataFrame with source, target, weight (no self-loops)
    """
    index_list = [k for k, v in sorted(index_map.items(), key=lambda x: x[1])]
    
    coo = matrix.tocoo()
    mask = coo.row < coo.col
    
    rows = coo.row[mask]
    cols = coo.col[mask]
    weights = coo.data[mask]
    
    edges_df = pd.DataFrame({
        'source': [index_list[i] for i in rows],
        'target': [index_list[j] for j in cols],
        'weight': weights.astype(int)
    })
    
    return edges_df


def filter_top_edges(edge_df: pd.DataFrame, top_n: int = None, min_weight: int = None) -> pd.DataFrame:
    """
    Filter edges by top N or minimum weight.
    
    Args:
        edge_df: DataFrame with source, target, weight
        top_n: Keep top N edges by weight
        min_weight: Minimum weight threshold
    
    Returns:
        Filtered DataFrame
    """
    result = edge_df.copy()
    
    if min_weight is not None:
        result = result[result['weight'] >= min_weight]
    
    if top_n is not None:
        result = result.nlargest(top_n, 'weight')
    
    return result
