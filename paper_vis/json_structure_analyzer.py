#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON结构分析器
读取JSON文件并输出其原始结构
"""

import json
import sys
from typing import Any
from pathlib import Path


class JSONStructureAnalyzer:
    """JSON结构分析器类"""
    
    def __init__(self):
        self.max_depth = 0
        self.total_keys = 0
    
    def analyze_structure(self, data: Any, depth: int = 0) -> str:
        """
        分析JSON数据结构并返回结构字符串（不显示具体内容）
        
        Args:
            data: JSON数据
            depth: 当前深度
        
        Returns:
            str: 结构字符串
        """
        self.max_depth = max(self.max_depth, depth)
        
        if isinstance(data, dict):
            if not data:
                return "{}"
            
            lines = ["{"]
            for key, value in data.items():
                child_structure = self.analyze_structure(value, depth + 1)
                lines.append(f"  {key}: {child_structure}")
                self.total_keys += 1
            lines.append("}")
            return "\n".join(lines)
            
        elif isinstance(data, list):
            if not data:
                return "[]"
            
            lines = ["["]
            if data:
                # 只显示第一个元素的结构
                first_structure = self.analyze_structure(data[0], depth + 1)
                lines.append(f"  {first_structure}")
                if len(data) > 1:
                    lines.append("  ...")
            lines.append("]")
            return "\n".join(lines)
            
        elif isinstance(data, str):
            return "string"
            
        elif isinstance(data, (int, float)):
            return "number"
            
        elif isinstance(data, bool):
            return "boolean"
            
        elif data is None:
            return "null"
            
        else:
            return "unknown"
    
    def analyze_file(self, file_path: str) -> bool:
        """
        分析JSON文件
        
        Args:
            file_path: JSON文件路径
        
        Returns:
            bool: 是否成功
        """
        try:
            # 检查文件是否存在
            if not Path(file_path).exists():
                print(f"文件不存在: {file_path}")
                return False
            
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 分析结构
            structure = self.analyze_structure(data)
            
            # 输出结构
            print(structure)
            
            return True
            
        except FileNotFoundError as e:
            print(f"文件错误: {e}")
            return False
            
        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            return False
            
        except Exception as e:
            print(f"未知错误: {e}")
            return False


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python json_structure_analyzer.py <json_file_path>")
        print("示例: python json_structure_analyzer.py data.json")
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyzer = JSONStructureAnalyzer()
    success = analyzer.analyze_file(file_path)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()