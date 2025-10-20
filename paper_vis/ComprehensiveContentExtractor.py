#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合内容提取器
整合标题规范化、标题映射和内容提取功能

功能流程：
1. 使用NormalizeHeadings.py获取清洗后的一级标题列表
2. 使用TitleMappingLLM.py将标题映射到四个标准泳道
3. 使用extractContentByHeading.py根据映射结果提取具体内容
4. 返回按泳道组织的完整内容字典
"""

import os
from typing import Dict, List
from NormalizeHeadings import HeadingNormalizer
from TitleMappingLLM import TitleMappingLLM
from extractContentByHeading import ContentExtractor
import json

class ComprehensiveContentExtractor:
    """综合内容提取器"""
    
    def __init__(self):
        """初始化综合提取器"""
        self.heading_normalizer = HeadingNormalizer()
        self.title_mapper = TitleMappingLLM()
        self.content_extractor = ContentExtractor()
    
    def extract_comprehensive_content(self, markdown_file_path: str, output_folder: str = None) -> Dict[str, str]:
        """
        综合内容提取主函数
        
        Args:
            markdown_file_path: Markdown文件路径
            output_folder: 输出文件夹路径，如果提供则生成origin_text.json文件
        
        Returns:
            Dict[str, str]: 按四个标准泳道组织的完整内容字典
        """
        try:
            # 步骤1: 获取清洗后的一级标题列表
            print("步骤1: 获取清洗后的一级标题列表...")
            h1_headings = self.heading_normalizer.process_markdown_file(markdown_file_path)
            
            if not h1_headings:
                print("错误: 未能提取到一级标题")
                return {}
            
            print(f"提取到 {len(h1_headings)} 个一级标题:")
            for i, heading in enumerate(h1_headings, 1):
                print(f"  {i}. {heading}")
            print()
            
            # 步骤2: 将标题映射到四个标准泳道
            print("步骤2: 将标题映射到四个标准泳道...")
            mapping_result = self.title_mapper.map_titles(h1_headings)
            
            if not mapping_result:
                print("错误: 标题映射失败")
                return {}
            
            print("映射结果:")
            for lane, titles in mapping_result.items():
                print(f"  {lane}: {titles}")
            print()
            
            # 步骤3: 根据映射结果提取具体内容
            print("步骤3: 提取各泳道的具体内容...")
            final_result = {}
            
            for lane_name, mapped_titles in mapping_result.items():
                print(f"处理泳道: {lane_name}")
                lane_content = ""
                
                for title in mapped_titles:
                    print(f"  提取标题: {title}")
                    content = self.content_extractor.extractContentByHeading(
                        h1_headings, markdown_file_path, title
                    )
                    
                    # 检查是否提取成功
                    if content.startswith("错误："):
                        print(f"    警告: {content}")
                        continue
                    
                    # 拼接内容
                    if lane_content:
                        lane_content += "\n\n" + content
                    else:
                        lane_content = content
                    
                    print(f"    成功提取 {len(content)} 个字符")
                
                final_result[lane_name] = lane_content
                print(f"  泳道 '{lane_name}' 总内容长度: {len(lane_content)} 字符")
                print()
            
            print("=== 综合内容提取完成 ===")
            
            # 如果提供了输出文件夹，生成origin_text.json文件
            if output_folder:
                origin_text_path = os.path.join(output_folder, "origin_text.json")
                try:
                    with open(origin_text_path, 'w', encoding='utf-8') as f:
                        json.dump(final_result, f, ensure_ascii=False, indent=2)
                    print(f"✓ 生成origin_text.json: {origin_text_path}")
                except Exception as e:
                    print(f"❌ 生成origin_text.json失败: {e}")
            
            return final_result
            
        except Exception as e:
            print(f"综合内容提取过程中发生异常: {e}")
            return {}

    def extract_comprehensive_content_from_string(self, markdown_content: str) -> Dict[str, str]:
        """
        从Markdown内容字符串中提取综合内容（不依赖文件）
        
        Args:
            markdown_content: Markdown内容字符串
        
        Returns:
            Dict[str, str]: 按四个标准泳道组织的完整内容字典
        """
        try:
            # 步骤1: 获取清洗后的一级标题列表
            print("步骤1: 获取清洗后的一级标题列表...")
            h1_headings = self.heading_normalizer.process_markdown_content(markdown_content)
            
            if not h1_headings:
                print("错误: 未能提取到一级标题")
                return {}
            
            print(f"提取到 {len(h1_headings)} 个一级标题:")
            for i, heading in enumerate(h1_headings, 1):
                print(f"  {i}. {heading}")
            print()
            
            # 步骤2: 将标题映射到四个标准泳道
            print("步骤2: 将标题映射到四个标准泳道...")
            mapping_result = self.title_mapper.map_titles(h1_headings)
            
            if not mapping_result:
                print("错误: 标题映射失败")
                return {}
            
            print("映射结果:")
            for lane, titles in mapping_result.items():
                print(f"  {lane}: {titles}")
            print()
            
            # 步骤3: 根据映射结果提取具体内容
            print("步骤3: 提取各泳道的具体内容...")
            final_result = {}
            
            for lane_name, mapped_titles in mapping_result.items():
                print(f"处理泳道: {lane_name}")
                lane_content = ""
                
                for title in mapped_titles:
                    print(f"  提取标题: {title}")
                    content = self.content_extractor.extractContentByHeadingFromContent(
                        h1_headings, markdown_content, title
                    )
                    
                    # 检查是否提取成功
                    if content.startswith("错误："):
                        print(f"    警告: {content}")
                        continue
                    
                    # 拼接内容
                    if lane_content:
                        lane_content += "\n\n" + content
                    else:
                        lane_content = content
                    
                    print(f"    成功提取 {len(content)} 个字符")
                
                final_result[lane_name] = lane_content
                print(f"  泳道 '{lane_name}' 总内容长度: {len(lane_content)} 字符")
                print()
            
            print("=== 综合内容提取完成 ===")
            return final_result
            
        except Exception as e:
            print(f"综合内容提取过程中发生异常: {e}")
            return {}
    
    def extract_content_with_summary(self, markdown_file_path: str) -> Dict[str, any]:
        """
        带摘要信息的综合内容提取
        
        Args:
            markdown_file_path: Markdown文件路径
        
        Returns:
            Dict[str, any]: 包含内容和摘要信息的字典
        """
        try:
            # 获取清洗后的一级标题列表
            h1_headings = self.heading_normalizer.process_markdown_file(markdown_file_path)
            
            if not h1_headings:
                return {
                    'success': False,
                    'error': '未能提取到一级标题',
                    'content': {}
                }
            
            # 将标题映射到四个标准泳道
            mapping_result = self.title_mapper.map_titles(h1_headings)
            
            if not mapping_result:
                return {
                    'success': False,
                    'error': '标题映射失败',
                    'content': {}
                }
            
            # 提取具体内容
            final_result = {}
            extraction_stats = {}
            
            for lane_name, mapped_titles in mapping_result.items():
                lane_content = ""
                extraction_stats[lane_name] = {
                    'titles_count': len(mapped_titles),
                    'titles': mapped_titles,
                    'successful_extractions': 0,
                    'failed_extractions': 0
                }
                
                for title in mapped_titles:
                    content = self.content_extractor.extractContentByHeading(
                        h1_headings, markdown_file_path, title
                    )
                    
                    if content.startswith("错误："):
                        extraction_stats[lane_name]['failed_extractions'] += 1
                        continue
                    
                    extraction_stats[lane_name]['successful_extractions'] += 1
                    
                    if lane_content:
                        lane_content += "\n\n" + content
                    else:
                        lane_content = content
                
                final_result[lane_name] = lane_content
            
            return {
                'success': True,
                'content': final_result,
                'summary': {
                    'total_h1_headings': len(h1_headings),
                    'h1_headings': h1_headings,
                    'mapping_result': mapping_result,
                    'extraction_stats': extraction_stats,
                    'file_path': markdown_file_path
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'处理过程中发生异常: {e}',
                'content': {}
            }


def main():
    """主函数，用于测试综合内容提取功能"""
    print("=== 综合内容提取器测试 ===")
    
    # 创建综合提取器实例
    extractor = ComprehensiveContentExtractor()
    
    # 测试文件路径（请根据实际情况修改）
    test_file_path = "/Users/xiaokong/task/2025/paper_vis/vis/md/2dbbabd2678ba74fcd9b08aadae975ae.md"
    
    # 检查文件是否存在
    if not os.path.exists(test_file_path):
        print(f"错误: 测试文件不存在: {test_file_path}")
        print("请修改 test_file_path 变量为实际存在的Markdown文件路径")
        return
    
    print(f"测试文件: {test_file_path}")
    print()
    
    # 执行综合内容提取
    result = extractor.extract_comprehensive_content(test_file_path)
    
    if result:
        print("=== 最终结果 ===")
        for lane_name, content in result.items():
            print(f"\n泳道: {lane_name}")
            print(f"内容长度: {len(content)} 字符")
            print(f"内容预览: {content}...")
            print("-" * 50)
    else:
        print("内容提取失败")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()
