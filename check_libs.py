#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查系统中可用的Python库
"""

print("检查Python环境...")

# 尝试导入常用库
try:
    import pandas
    print("[OK] pandas 已安装")
except ImportError:
    print("[ERROR] pandas 未安装")

try:
    import requests
    print("[OK] requests 已安装")
except ImportError:
    print("[ERROR] requests 未安装")

try:
    import json
    print("[OK] json 已安装")
except ImportError:
    print("[ERROR] json 未安装")

try:
    import os
    print("[OK] os 已安装")
except ImportError:
    print("[ERROR] os 未安装")

try:
    from configparser import ConfigParser
    print("[OK] configparser 已安装")
except ImportError:
    print("[ERROR] configparser 未安装")

try:
    import argparse
    print("[OK] argparse 已安装")
except ImportError:
    print("[ERROR] argparse 未安装")

try:
    import networkx
    print("[OK] networkx 已安装")
except ImportError:
    print("[ERROR] networkx 未安装")

try:
    import matplotlib
    print("[OK] matplotlib 已安装")
except ImportError:
    print("[ERROR] matplotlib 未安装")

print("检查完成!")