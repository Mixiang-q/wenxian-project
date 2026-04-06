#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分析模块
用于对纳米线神经突触器件相关文献数据进行计量学分析
"""

import csv
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import os


def load_data(data_file='data/raw/literature_data.csv'):
    """
    加载数据
    """
    data = []
    with open(data_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    return data


def publication_trend_analysis(data):
    """
     publications trend analysis
    """
    print("\n=== 出版物趋势分析 ===")
    # 统计每年的出版物数量
    yearly_counts = Counter()
    for item in data:
        if item.get('year'):
            yearly_counts[item['year']] += 1
    
    # 按年份排序
    sorted_years = sorted(yearly_counts.keys())
    for year in sorted_years:
        print(f"{year}: {yearly_counts[year]}")
    
    # 可视化
    plt.figure(figsize=(10, 6))
    plt.bar(sorted_years, [yearly_counts[year] for year in sorted_years])
    plt.title('Publications by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Publications')
    plt.tight_layout()
    os.makedirs('outputs/figures', exist_ok=True)
    plt.savefig('outputs/figures/publication_trend.png')
    print("趋势图已保存至 outputs/figures/publication_trend.png")


def journal_analysis(data):
    """
    期刊分析
    """
    print("\n=== 期刊分析 ===")
    # 统计期刊出现次数
    journal_counts = Counter()
    for item in data:
        if item.get('journal'):
            journal_counts[item['journal']] += 1
    
    # 获取前10个期刊
    top_journals = journal_counts.most_common(10)
    for journal, count in top_journals:
        print(f"{journal}: {count}")
    
    # 可视化
    if top_journals:
        plt.figure(figsize=(12, 8))
        journals, counts = zip(*top_journals)
        plt.barh(journals, counts)
        plt.title('Top 10 Journals')
        plt.xlabel('Number of Publications')
        plt.tight_layout()
        plt.savefig('outputs/figures/top_journals.png')
        print("期刊分析图已保存至 outputs/figures/top_journals.png")
    else:
        print("没有足够的期刊数据进行可视化")


def author_analysis(data):
    """
    作者分析
    """
    print("\n=== 作者分析 ===")
    # 提取所有作者
    all_authors = []
    for item in data:
        if item.get('authors'):
            authors_list = [author.strip() for author in item['authors'].split(',')]
            all_authors.extend(authors_list)
    
    # 统计作者出现次数
    author_counts = Counter(all_authors)
    top_authors = author_counts.most_common(10)
    print("Top 10 Authors:")
    for author, count in top_authors:
        print(f"{author}: {count}")
    
    # 可视化
    plt.figure(figsize=(12, 8))
    authors, counts = zip(*top_authors)
    plt.barh(authors, counts)
    plt.title('Top 10 Authors')
    plt.xlabel('Number of Publications')
    plt.tight_layout()
    plt.savefig('outputs/figures/top_authors.png')
    print("作者分析图已保存至 outputs/figures/top_authors.png")


def keyword_analysis(data):
    """
    关键词分析
    """
    print("\n=== 关键词分析 ===")
    # 提取所有关键词
    all_keywords = []
    for item in data:
        if item.get('keywords'):
            keywords_list = [keyword.strip() for keyword in item['keywords'].split(',')]
            all_keywords.extend(keywords_list)
    
    # 统计关键词出现次数
    keyword_counts = Counter(all_keywords)
    top_keywords = keyword_counts.most_common(15)
    print("Top 15 Keywords:")
    for keyword, count in top_keywords:
        print(f"{keyword}: {count}")
    
    # 可视化
    if top_keywords:
        plt.figure(figsize=(14, 10))
        keywords, counts = zip(*top_keywords)
        plt.barh(keywords, counts)
        plt.title('Top 15 Keywords')
        plt.xlabel('Number of Occurrences')
        plt.tight_layout()
        plt.savefig('outputs/figures/top_keywords.png')
        print("关键词分析图已保存至 outputs/figures/top_keywords.png")
    else:
        print("没有足够的关键词数据进行可视化")


def co_occurrence_analysis(data):
    """
    关键词共现分析
    """
    print("\n=== 关键词共现分析 ===")
    # 构建关键词共现网络
    G = nx.Graph()
    
    for item in data:
        if item.get('keywords'):
            keywords_list = [keyword.strip() for keyword in item['keywords'].split(',')]
            # 添加节点
            for keyword in keywords_list:
                if keyword not in G.nodes():
                    G.add_node(keyword)
            # 添加边
            for i in range(len(keywords_list)):
                for j in range(i+1, len(keywords_list)):
                    if G.has_edge(keywords_list[i], keywords_list[j]):
                        G[keywords_list[i]][keywords_list[j]]['weight'] += 1
                    else:
                        G.add_edge(keywords_list[i], keywords_list[j], weight=1)
    
    # 过滤掉权重较低的边
    edges_to_remove = [(u, v) for u, v, w in G.edges(data='weight') if w < 2]
    G.remove_edges_from(edges_to_remove)
    
    # 过滤掉孤立节点
    nodes_to_remove = [node for node in G.nodes() if G.degree(node) == 0]
    G.remove_nodes_from(nodes_to_remove)
    
    # 可视化
    if G.nodes():
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(G, k=0.3, iterations=50)
        weights = [G[u][v]['weight'] for u, v in G.edges()]
        nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', 
                font_size=10, edge_color='gray', width=weights)
        plt.title('Keyword Co-occurrence Network')
        plt.tight_layout()
        plt.savefig('outputs/figures/keyword_cooccurrence.png')
        print("关键词共现网络图已保存至 outputs/figures/keyword_cooccurrence.png")
    else:
        print("没有足够的关键词数据进行共现分析")


def main():
    """
    主函数
    """
    # 加载数据
    data = load_data()
    print(f"数据加载完成，共 {len(data)} 条文献")
    
    # 执行各项分析
    publication_trend_analysis(data)
    journal_analysis(data)
    author_analysis(data)
    keyword_analysis(data)
    co_occurrence_analysis(data)
    
    print("\n=== 分析完成 ===")


if __name__ == '__main__':
    main()
