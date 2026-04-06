#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主脚本
用于执行整个文献计量学分析工作流程
"""

import os
import sys
import argparse


def main():
    """
    主函数
    """
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='纳米线神经突触器件文献计量学分析')
    parser.add_argument('--acquire', action='store_true', help='获取数据')
    parser.add_argument('--analyze', action='store_true', help='分析数据')
    parser.add_argument('--all', action='store_true', help='执行完整流程')
    parser.add_argument('--database', choices=['wos', 'scopus', 'openalex'], default='openalex', 
                        help='选择数据库 (默认: openalex)')
    parser.add_argument('--query', type=str, default='nanowire synaptic device',
                      help='搜索查询 (默认: nanowire synaptic device)')
    parser.add_argument('--start-year', type=int, default=2021,
                      help='开始年份 (默认: 2021)')
    parser.add_argument('--end-year', type=int, default=2025,
                      help='结束年份 (默认: 2025)')
    args = parser.parse_args()
    
    # 执行数据获取
    if args.acquire or args.all:
        print("=== 开始获取数据 ===")
        try:
            import data_acquisition
            # 传递参数
            import subprocess
            cmd = [sys.executable, 'src/data_acquisition.py', '--database', args.database]
            if args.query:
                cmd.extend(['--query', args.query])
            if args.start_year:
                cmd.extend(['--start-year', str(args.start_year)])
            if args.end_year:
                cmd.extend(['--end-year', str(args.end_year)])
            subprocess.run(cmd, check=True)
        except Exception as e:
            print(f"数据获取失败: {e}")
            sys.exit(1)
    
    # 执行数据分析
    if args.analyze or args.all:
        print("\n=== 开始分析数据 ===")
        try:
            import data_analysis
            data_analysis.main()
        except Exception as e:
            print(f"数据分析失败: {e}")
            sys.exit(1)
    
    # 如果没有指定任何参数，显示帮助信息
    if not any([args.acquire, args.analyze, args.all]):
        parser.print_help()


if __name__ == '__main__':
    main()
