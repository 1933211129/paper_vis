#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据标题提取Markdown文件内容的工具

功能：
- 根据标题列表和指定标题，提取该标题到下一个标题之间的内容
- 支持处理最后一个标题的情况（提取到文件结束）
"""

import os
import re
from typing import List, Optional


class ContentExtractor:
    """根据标题提取Markdown文件内容的类"""
    
    def __init__(self):
        """初始化内容提取器"""
        pass
    
    def _normalizeHeading(self, heading: str) -> str:
        """
        标准化标题格式，用于灵活匹配
        
        Args:
            heading: 原始标题
        
        Returns:
            str: 标准化后的标题
        """
        if not heading:
            return ""
        
        # 去除首尾空格
        normalized = heading.strip()
        
        # 如果标题以#开头，保留#和后面的内容
        if normalized.startswith('#'):
            # 提取#后面的内容
            content = normalized[1:].strip()
            return f"#{content}"
        else:
            # 如果没有#，直接返回去除空格后的内容
            return normalized
    
    def _extractHeadingContent(self, heading: str) -> str:
        """
        提取标题的核心内容（去除#、序号等）
        
        Args:
            heading: 标题
        
        Returns:
            str: 核心内容
        """
        if not heading:
            return ""
        
        # 去除首尾空格
        content = heading.strip()
        
        # 去除开头的#号
        if content.startswith('#'):
            content = content[1:].strip()
        
        # 去除开头的序号（如 "1. "、"2. "等）
        # 匹配模式：数字 + 点 + 空格
        content = re.sub(r'^\d+\.\s*', '', content)
        
        # 去除多余空格
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content
    
    def _extractCleanWords(self, heading: str) -> str:
        """
        提取标题中的干净单词（英文+中文），用于匹配
        
        Args:
            heading: 标题
        
        Returns:
            str: 干净的单词字符串
        """
        if not heading:
            return ""
        
        # 去除首尾空格
        content = heading.strip()
        
        # 去除开头的#号
        if content.startswith('#'):
            content = content[1:].strip()
        
        # 去除开头的序号（如 "1. "、"2. "等）
        content = re.sub(r'^\d+\.\s*', '', content)
        
        # 只保留英文单词、中文汉字、数字和基本标点
        # 匹配：英文字母、中文汉字、数字、空格、连字符、下划线
        clean_content = re.sub(r'[^\w\s\u4e00-\u9fff\-]', '', content)
        
        # 去除多余空格并转换为小写
        clean_content = re.sub(r'\s+', ' ', clean_content).strip().lower()
        
        return clean_content
    
    def _isHeadingMatch(self, heading1: str, heading2: str) -> bool:
        """
        判断两个标题是否匹配（使用干净单词匹配）
        
        Args:
            heading1: 标题1
            heading2: 标题2
        
        Returns:
            bool: 是否匹配
        """
        # 提取干净单词进行匹配
        clean1 = self._extractCleanWords(heading1)
        clean2 = self._extractCleanWords(heading2)
        
        # 如果任一为空，不匹配
        if not clean1 or not clean2:
            return False
        
        # 干净单词匹配
        return clean1 == clean2
    
    def extractContentByHeading(self, headingList: List[str], filePath: str, targetHeading: str) -> str:
        """
        根据标题列表和指定标题提取内容
        
        Args:
            headingList: 标题列表，例如 ['# Abstract', '# 1. Introduction', '# 2. Methods']
            filePath: Markdown文件路径
            targetHeading: 目标标题，例如 "# 5. Conclusion"
        
        Returns:
            str: 提取的内容文本
        """
        try:
            # 读取文件内容
            with open(filePath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 按行分割内容
            lines = content.split('\n')
            
            # 找到目标标题在标题列表中的位置
            targetIndex = self._findHeadingIndex(headingList, targetHeading)
            if targetIndex == -1:
                return f"错误：在标题列表中未找到目标标题 '{targetHeading}'"
            
            # 找到目标标题在文件中的位置
            targetLineIndex = self._findHeadingInFile(lines, targetHeading)
            if targetLineIndex == -1:
                return f"错误：在文件中未找到目标标题 '{targetHeading}'"
            
            # 确定结束位置
            if targetIndex == len(headingList) - 1:
                # 如果是最后一个标题，提取到文件结束
                endLineIndex = len(lines)
            else:
                # 找到下一个标题在文件中的位置
                nextHeading = headingList[targetIndex + 1]
                endLineIndex = self._findHeadingInFile(lines, nextHeading)
                if endLineIndex == -1:
                    return f"错误：在文件中未找到下一个标题 '{nextHeading}'"
            
            # 提取内容
            extractedLines = lines[targetLineIndex:endLineIndex]
            extractedContent = '\n'.join(extractedLines)
            
            return extractedContent.strip()
            
        except FileNotFoundError:
            return f"错误：文件 '{filePath}' 不存在"
        except Exception as e:
            return f"错误：处理文件时发生异常 - {str(e)}"

    def extractContentByHeadingFromContent(self, headingList: List[str], markdownContent: str, targetHeading: str) -> str:
        """
        根据标题列表和指定标题从Markdown内容中提取内容（不依赖文件）
        
        Args:
            headingList: 标题列表，例如 ['# Abstract', '# 1. Introduction', '# 2. Methods']
            markdownContent: Markdown内容字符串
            targetHeading: 目标标题，例如 "# 5. Conclusion"
        
        Returns:
            str: 提取的内容文本
        """
        try:
            # 按行分割内容
            lines = markdownContent.split('\n')
            
            # 找到目标标题在标题列表中的位置
            targetIndex = self._findHeadingIndex(headingList, targetHeading)
            if targetIndex == -1:
                return f"错误：在标题列表中未找到目标标题 '{targetHeading}'"
            
            # 找到目标标题在内容中的位置
            targetLineIndex = self._findHeadingInFile(lines, targetHeading)
            if targetLineIndex == -1:
                return f"错误：在内容中未找到目标标题 '{targetHeading}'"
            
            # 确定结束位置
            if targetIndex == len(headingList) - 1:
                # 如果是最后一个标题，提取到内容结束
                endLineIndex = len(lines)
            else:
                # 找到下一个标题在内容中的位置
                nextHeading = headingList[targetIndex + 1]
                endLineIndex = self._findHeadingInFile(lines, nextHeading)
                if endLineIndex == -1:
                    return f"错误：在内容中未找到下一个标题 '{nextHeading}'"
            
            # 提取内容
            extractedLines = lines[targetLineIndex:endLineIndex]
            extractedContent = '\n'.join(extractedLines)
            
            return extractedContent.strip()
            
        except Exception as e:
            return f"错误：处理内容时发生异常 - {str(e)}"
    
    def _findHeadingIndex(self, headingList: List[str], targetHeading: str) -> int:
        """
        在标题列表中找到目标标题的索引（支持灵活匹配）
        
        Args:
            headingList: 标题列表
            targetHeading: 目标标题
        
        Returns:
            int: 标题索引，未找到返回-1
        """
        for i, heading in enumerate(headingList):
            if self._isHeadingMatch(heading, targetHeading):
                return i
        return -1
    
    def _findHeadingInFile(self, lines: List[str], heading: str) -> int:
        """
        在文件行中找到标题的位置（支持灵活匹配）
        
        Args:
            lines: 文件行列表
            heading: 要查找的标题
        
        Returns:
            int: 行索引，未找到返回-1
        """
        for i, line in enumerate(lines):
            if self._isHeadingMatch(line, heading):
                return i
        return -1
    
    def extractContentByHeadingWithDebug(self, headingList: List[str], filePath: str, targetHeading: str) -> dict:
        """
        带调试信息的提取内容方法
        
        Args:
            headingList: 标题列表
            filePath: Markdown文件路径
            targetHeading: 目标标题
        
        Returns:
            dict: 包含结果和调试信息的字典
        """
        result = {
            'success': False,
            'content': '',
            'debug_info': {
                'target_heading': targetHeading,
                'target_index': -1,
                'next_heading': '',
                'start_line': -1,
                'end_line': -1,
                'total_lines': 0,
                'error': ''
            }
        }
        
        try:
            # 读取文件内容
            with open(filePath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            lines = content.split('\n')
            result['debug_info']['total_lines'] = len(lines)
            
            # 找到目标标题在标题列表中的位置
            targetIndex = self._findHeadingIndex(headingList, targetHeading)
            result['debug_info']['target_index'] = targetIndex
            
            if targetIndex == -1:
                result['debug_info']['error'] = f"在标题列表中未找到目标标题 '{targetHeading}'"
                return result
            
            # 找到目标标题在文件中的位置
            targetLineIndex = self._findHeadingInFile(lines, targetHeading)
            result['debug_info']['start_line'] = targetLineIndex
            
            if targetLineIndex == -1:
                result['debug_info']['error'] = f"在文件中未找到目标标题 '{targetHeading}'"
                return result
            
            # 确定结束位置
            if targetIndex == len(headingList) - 1:
                # 最后一个标题
                endLineIndex = len(lines)
                result['debug_info']['next_heading'] = '文件结束'
            else:
                # 找到下一个标题
                nextHeading = headingList[targetIndex + 1]
                result['debug_info']['next_heading'] = nextHeading
                endLineIndex = self._findHeadingInFile(lines, nextHeading)
                
                if endLineIndex == -1:
                    result['debug_info']['error'] = f"在文件中未找到下一个标题 '{nextHeading}'"
                    return result
            
            result['debug_info']['end_line'] = endLineIndex
            
            # 提取内容
            extractedLines = lines[targetLineIndex:endLineIndex]
            extractedContent = '\n'.join(extractedLines)
            
            result['success'] = True
            result['content'] = extractedContent.strip()
            
            return result
            
        except FileNotFoundError:
            result['debug_info']['error'] = f"文件 '{filePath}' 不存在"
            return result
        except Exception as e:
            result['debug_info']['error'] = f"处理文件时发生异常 - {str(e)}"
            return result


# def main():
#     """主函数，用于测试功能"""
#     extractor = ContentExtractor()
    
#     # 测试数据
#     headingList = [
#         '# A Q-learning approach to the continuous control problem of robot inverted pendulum balancing',
#         '# Corresponding Author:',
#         '# A Q-learning approach to the continuous control problem of robot inverted pendulum balancing',
#         '# Abstract',
#         '# 1. Introduction',
#         '# 2. Proposed approach and background',
#         '# 3. Methodologies',
#         '# 4. Results and discussion',
#         '# 5. Conclusion',
#         '# Acknowledgements',
#         '# References'
#     ]
    
#     filePath = "/Users/xiaokong/task/2025/paper_vis/vis/md/2dbbabd2678ba74fcd9b08aadae975ae.md"
#     targetHeading = "# 5. Conclusion"
    
#     print("=== 测试内容提取功能 ===")
#     print(f"目标标题: {targetHeading}")
#     print(f"文件路径: {filePath}")
#     print()
    
#     # 测试基本功能
#     content = extractor.extractContentByHeading(headingList, filePath, targetHeading)
#     print("=== 提取的内容 ===")
#     print(content)
#     print()
    
#     # 测试调试功能
#     debugResult = extractor.extractContentByHeadingWithDebug(headingList, filePath, targetHeading)
#     print("=== 调试信息 ===")
#     print(f"成功: {debugResult['success']}")
#     print(f"目标标题: {debugResult['debug_info']['target_heading']}")
#     print(f"目标索引: {debugResult['debug_info']['target_index']}")
#     print(f"下一个标题: {debugResult['debug_info']['next_heading']}")
#     print(f"开始行: {debugResult['debug_info']['start_line']}")
#     print(f"结束行: {debugResult['debug_info']['end_line']}")
#     print(f"总行数: {debugResult['debug_info']['total_lines']}")
#     if debugResult['debug_info']['error']:
#         print(f"错误: {debugResult['debug_info']['error']}")


# if __name__ == "__main__":
#     main()
