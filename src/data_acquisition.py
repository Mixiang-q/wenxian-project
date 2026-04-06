#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取模块
用于从Web of Science或Scopus数据库获取纳米线神经突触器件相关文献数据
"""

import requests
import json
import os
from configparser import ConfigParser
import argparse
import csv
import pandas as pd
import yaml


def load_config(config_file='config.ini'):
    """
    加载配置文件，获取API密钥
    """
    config = ConfigParser()
    config.read(config_file)
    return config


def load_yaml_config(yaml_file='config/query.yaml'):
    """
    加载YAML配置文件，获取检索式和相关配置
    """
    with open(yaml_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config





def fetch_from_wos(query, time_window, fields):
    """
    从Web of Science获取数据
    注意：实际使用需要配置API密钥
    """
    print(f"从Web of Science获取数据，查询: {query}")
    print(f"时间范围: {time_window[0]}-{time_window[1]}")
    
    # 加载API密钥
    config = load_config()
    api_key = config.get('WebOfScience', 'api_key', fallback='your_api_key_here')
    
    if api_key == 'your_api_key_here':
        print("错误: 请在config.ini文件中配置Web of Science API密钥")
        return pd.DataFrame()
    
    # Web of Science API endpoint
    url = "https://api.clarivate.com/api/wos"
    
    # 构建查询
    search_query = f"{query} AND PY={time_window[0]}-{time_window[1]}"
    
    # API请求参数
    params = {
        "databaseId": "WOS",
        "count": 100,  # 每次请求的记录数
        "firstRecord": 1,  # 起始记录
        "usrQuery": search_query
    }
    
    # 请求头
    headers = {
        "X-APIKey": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        # 发送请求
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # 检查响应状态
        
        # 解析响应
        data = response.json()
        
        # 提取文献数据
        records = data.get('Data', {}).get('Records', {}).get('records', [])
        
        # 转换为DataFrame
        literature_data = []
        for record in records:
            title = record.get('title', {}).get('title', [''])[0]
            authors = ', '.join(record.get('authors', {}).get('author', []))
            year = record.get('pub_info', {}).get('pubyear', '')
            journal = record.get('title', {}).get('abbrev_iso', '')
            abstract = record.get('abstracts', {}).get('abstract', [{}])[0].get('abstract_text', '')
            keywords = ', '.join(record.get('keywords', {}).get('keyword', []))
            
            literature_data.append({
                'title': title,
                'authors': authors,
                'year': year,
                'journal': journal,
                'abstract': abstract,
                'keywords': keywords
            })
        
        df = pd.DataFrame(literature_data)
        print(f"从Web of Science API成功获取 {len(df)} 条文献")
        return df
    except Exception as e:
        print(f"Web of Science API请求失败: {str(e)}")
        return pd.DataFrame()





def fetch_from_scopus(query, time_window, fields):
    """
    从Scopus获取数据
    注意：实际使用需要配置API密钥
    """
    print(f"从Scopus获取数据，查询: {query}")
    print(f"时间范围: {time_window[0]}-{time_window[1]}")
    
    # 加载API密钥
    config = load_config()
    api_key = config.get('Scopus', 'api_key', fallback='your_api_key_here')
    
    if api_key == 'your_api_key_here':
        print("错误: 请在config.ini文件中配置Scopus API密钥")
        return pd.DataFrame()
    
    # Scopus API endpoint
    url = "https://api.elsevier.com/content/search/scopus"
    
    # 构建查询
    search_query = f"TITLE-ABS-KEY({query}) AND PUBYEAR > {time_window[0]-1} AND PUBYEAR < {time_window[1]+1}"
    
    # API请求参数
    params = {
        "query": search_query,
        "count": 100,  # 每次请求的记录数
        "start": 0,  # 起始记录
        "field": "title,authors,publicationName,prism:coverDate,abstract,keywords"
    }
    
    # 请求头
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }
    
    try:
        # 发送请求
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # 检查响应状态
        
        # 解析响应
        data = response.json()
        
        # 提取文献数据
        records = data.get('search-results', {}).get('entry', [])
        
        # 转换为DataFrame
        literature_data = []
        for record in records:
            title = record.get('dc:title', '')
            authors = ', '.join([author.get('$', '') for author in record.get('author', [])])
            year = record.get('prism:coverDate', '')[:4]
            journal = record.get('prism:publicationName', '')
            abstract = record.get('dc:description', '')
            keywords = ', '.join(record.get('authkeywords', '').split('|'))
            
            literature_data.append({
                'title': title,
                'authors': authors,
                'year': year,
                'journal': journal,
                'abstract': abstract,
                'keywords': keywords
            })
        
        df = pd.DataFrame(literature_data)
        print(f"从Scopus API成功获取 {len(df)} 条文献")
        return df
    except Exception as e:
        print(f"Scopus API请求失败: {str(e)}")
        return pd.DataFrame()





def reconstruct_abstract(inv_index):
    """
    从OpenAlex的abstract_inverted_index还原摘要
    """
    if not inv_index:
        return ""
    words = []
    for word, positions in inv_index.items():
        for pos in positions:
            words.append((pos, word))
    words.sort()
    return ' '.join([w for _, w in words])

def fetch_from_openalex(query, time_window, fields):
    """
    从OpenAlex获取数据
    OpenAlex不需要API密钥，但建议添加邮件地址以获得更好的访问速度
    """
    print(f"从OpenAlex获取数据")
    print(f"时间范围: {time_window[0]}-{time_window[1]}")
    
    # 加载配置
    config = load_config()
    email = config.get('OpenAlex', 'email', fallback='')
    
    # 使用用户传入的查询，而不是硬编码
    simple_query = query
    print(f"使用查询: {simple_query}")
    
    if email:
        print(f"使用邮件地址: {email} (有助于提高API访问速度)")
    else:
        print("警告: 建议在config.ini文件中配置email以获得更好的API访问速度")
    
    # 构建查询URL - 直接在URL中构建查询
    base_url = "https://api.openalex.org/works"
    
    # 构建查询参数 - 使用字段限定检索，拆分关键词
    # OpenAlex不支持复杂布尔表达式，需要拆分关键词
    keywords = ["nanowire", "synaptic", "memristor", "neuromorphic"]
    # API做宽筛，使用OR连接关键词
    filter_expression = " OR ".join([f"title.search:{kw}" for kw in keywords])
    
    query_params = {
        "filter": filter_expression,
        "per-page": 200,  # 每页200条
        "page": 1,
        "sort": "cited_by_count:desc"  # 按引用数降序排序，高被引论文优先
    }
    
    # 请求头
    headers = {}
    if email:
        headers["User-Agent"] = f"mailto:{email}"
    
    all_records = []
    max_pages = 10  # 最多获取5页数据，共1000条
    current_page = 1
    
    # 定义相关关键词，用于过滤结果
    relevant_keywords = [
        'nanowire', 'synaptic', 'synapse', 'neuromorphic', 
        'plasticity', 'optoelectronic', 'memristor'
    ]
    
    try:
        while current_page <= max_pages:
            print(f"获取第 {current_page} 页数据...")
            query_params["page"] = current_page
            
            # 发送请求，添加超时设置
            response = requests.get(base_url, params=query_params, headers=headers, timeout=30)
            response.raise_for_status()  # 检查响应状态
            
            # 解析响应
            data = response.json()
            
            # 提取文献数据
            records = data.get('results', [])
            
            # 过滤相关记录
            for record in records:
                # 检查标题和摘要中是否包含相关关键词
                title = record.get('title', '').lower()
                abstract_inv_index = record.get('abstract_inverted_index', {})
                abstract = reconstruct_abstract(abstract_inv_index).lower()
                
                # 检查是否包含任何相关关键词
                is_relevant = False
                for keyword in relevant_keywords:
                    if keyword in title or keyword in abstract:
                        is_relevant = True
                        break
                
                # 暂时移除引用数筛选，先获取更多文献
                if is_relevant:
                    all_records.append(record)
            
            # 检查是否还有更多页面
            if len(records) < 200:
                break
            
            current_page += 1
        
        # 过滤年份
        filtered_records = []
        for record in all_records:
            year = record.get('publication_year', 0)
            if time_window[0] <= year <= time_window[1]:
                filtered_records.append(record)
        
        # 转换为DataFrame
        literature_data = []
        for record in filtered_records:
            title = record.get('title', '')
            authors = ', '.join([author.get('author', {}).get('display_name', '') for author in record.get('authorships', [])])
            year = record.get('publication_year', '')
            journal = record.get('host_venue', {}).get('display_name', '')
            abstract = reconstruct_abstract(record.get('abstract_inverted_index', {}))
            
            # 处理关键词，确保只处理字符串类型
            keywords_list = record.get('keywords', [])
            # 检查keywords_list的类型
            if isinstance(keywords_list, list):
                # 过滤出字符串类型的关键词
                string_keywords = []
                for keyword in keywords_list:
                    if isinstance(keyword, str):
                        string_keywords.append(keyword)
                    elif isinstance(keyword, dict) and 'keyword' in keyword:
                        string_keywords.append(keyword['keyword'])
                keywords = ', '.join(string_keywords[:10])  # 最多取10个关键词
            else:
                # 尝试从标题和摘要中提取关键词，优先从标题中提取
                text = (title + ' ' + abstract).lower()
                extracted_keywords = []
                for keyword in relevant_keywords:
                    if keyword in text:
                        extracted_keywords.append(keyword)
                # 如果从标题和摘要中没有提取到关键词，尝试从标题中提取更具体的关键词
                if not extracted_keywords:
                    # 从标题中提取可能的关键词
                    title_words = title.split()
                    for word in title_words:
                        # 过滤掉常见的虚词
                        if len(word) > 3 and word not in ['for', 'with', 'from', 'using', 'based', 'device', 'devices']:
                            extracted_keywords.append(word)
                keywords = ', '.join(extracted_keywords[:10])
            
            # 获取引用数
            citation = record.get('cited_by_count', 0)
            
            literature_data.append({
                'title': title,
                'authors': authors,
                'year': year,
                'journal': journal,
                'abstract': abstract,
                'keywords': keywords,
                'citation': citation
            })
        
        df = pd.DataFrame(literature_data)
        # 去重
        df = df.drop_duplicates(subset=['title'])
        print(f"从OpenAlex API成功获取 {len(df)} 条相关文献")
        return df
    except requests.exceptions.SSLError as e:
        print(f"OpenAlex API请求失败 (SSL错误): {str(e)}")
        print("尝试使用备用方法获取数据...")
        # 尝试使用更简单的查询
        try:
            # 使用备用查询方式，拆分关键词
            backup_keywords = ["nanowire", "synaptic", "device"]
            backup_filter = " OR ".join([f"title.search:{kw}" for kw in backup_keywords])
            print(f"使用备用查询: nanowire OR synaptic OR device")
            query_params["filter"] = backup_filter
            query_params["sort"] = "cited_by_count:desc"  # 按引用数降序排序
            response = requests.get(base_url, params=query_params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            records = data.get('results', [])
            
            # 过滤相关记录
            relevant_records = []
            for record in records:
                title = record.get('title', '').lower()
                abstract = reconstruct_abstract(record.get('abstract_inverted_index', {})).lower()
                is_relevant = False
                for keyword in relevant_keywords:
                    if keyword in title or keyword in abstract:
                        is_relevant = True
                        break
                # 暂时移除引用数筛选，先获取更多文献
                if is_relevant:
                    relevant_records.append(record)
            
            filtered_records = [r for r in relevant_records if time_window[0] <= r.get('publication_year', 0) <= time_window[1]]
            
            literature_data = []
            for record in filtered_records:
                title = record.get('title', '')
                authors = ', '.join([author.get('author', {}).get('display_name', '') for author in record.get('authorships', [])])
                year = record.get('publication_year', '')
                journal = record.get('host_venue', {}).get('display_name', '')
                abstract = reconstruct_abstract(record.get('abstract_inverted_index', {}))
                keywords_list = record.get('keywords', [])
                
                if isinstance(keywords_list, list):
                    string_keywords = []
                    for keyword in keywords_list:
                        if isinstance(keyword, str):
                            string_keywords.append(keyword)
                        elif isinstance(keyword, dict) and 'keyword' in keyword:
                            string_keywords.append(keyword['keyword'])
                    keywords = ', '.join(string_keywords[:10])
                else:
                    # 尝试从标题和摘要中提取关键词，优先从标题中提取
                    text = (title + ' ' + abstract).lower()
                    extracted_keywords = []
                    for keyword in relevant_keywords:
                        if keyword in text:
                            extracted_keywords.append(keyword)
                    # 如果从标题和摘要中没有提取到关键词，尝试从标题中提取更具体的关键词
                    if not extracted_keywords:
                        # 从标题中提取可能的关键词
                        title_words = title.split()
                        for word in title_words:
                            # 过滤掉常见的虚词
                            if len(word) > 3 and word not in ['for', 'with', 'from', 'using', 'based', 'device', 'devices']:
                                extracted_keywords.append(word)
                    keywords = ', '.join(extracted_keywords[:10])
                
                # 获取引用数
                citation = record.get('cited_by_count', 0)
                
                literature_data.append({
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'journal': journal,
                    'abstract': abstract,
                    'keywords': keywords,
                    'citation': citation
                })
            
            df = pd.DataFrame(literature_data)
            # 去重
            df = df.drop_duplicates(subset=['title'])
            print(f"从OpenAlex API成功获取 {len(df)} 条相关文献")
            return df
        except Exception as e2:
            print(f"备用方法也失败: {str(e2)}")
            return pd.DataFrame()
    except Exception as e:
        print(f"OpenAlex API请求失败: {str(e)}")
        return pd.DataFrame()


def main():
    """
    主函数
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='从指定数据库获取纳米线神经突触器件相关文献数据')
    parser.add_argument('--database', choices=['wos', 'scopus', 'openalex'], default='openalex', 
                        help='选择数据库 (默认: openalex)')
    parser.add_argument('--query', type=str, default='',
                      help='搜索查询 (默认使用配置文件中的布尔检索表达式)')
    parser.add_argument('--start-year', type=int, default=2021,
                      help='开始年份 (默认: 2021)')
    parser.add_argument('--end-year', type=int, default=2025,
                      help='结束年份 (默认: 2025)')
    args = parser.parse_args()
    
    # 加载YAML配置文件
    yaml_config = load_yaml_config()
    
    # 定义查询参数
    if args.query:
        query = args.query
    else:
        # 使用配置文件中的布尔检索表达式作为默认查询
        query = yaml_config.get('boolean_expression', 'nanowire synaptic device')
    time_window = (args.start_year, args.end_year)
    fields = ['title', 'authors', 'year', 'journal', 'abstract', 'keywords']
    
    # 从指定数据库获取数据
    if args.database == 'wos':
        data = fetch_from_wos(query, time_window, fields)
    elif args.database == 'scopus':
        data = fetch_from_scopus(query, time_window, fields)
    else:  # openalex
        data = fetch_from_openalex(query, time_window, fields)
    
    # 保存数据
    os.makedirs('data/raw', exist_ok=True)
    data.to_csv('data/raw/literature_data.csv', index=False, encoding='utf-8-sig')
    
    print(f"从{args.database.upper()}数据库获取数据完成，共获取 {len(data)} 条文献")


if __name__ == '__main__':
    main()
