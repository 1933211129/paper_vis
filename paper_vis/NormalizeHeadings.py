# 标题层级规范化系统
import re
from pathlib import Path
from typing import List, Tuple, Dict

class HeadingNormalizer:
    """标题层级规范化器"""
    
    def __init__(self):
        """初始化规范化器"""
        # 定义已知的无编号一级标题关键词
        self.unnumbered_h1_keywords = [
            'Abstract', 'Introduction', 'Conclusion', 'References', 'Appendix',
            'Acknowledgments', 'Acknowledgements', 'Bibliography', 'Index',
            'Preface', 'Foreword', 'Summary', 'Executive Summary',
            'Table of Contents', 'List of Figures', 'List of Tables',
            'Nomenclature', 'Glossary', 'Abbreviations'
        ]
        
        # 编译正则表达式模式（按优先级排序）
        self.patterns = [
            # 三级标题: # 1.1.1. 标题
            (r'^(\s*)#\s+(\d+\.\d+\.\d+\.\s+.*)$', r'\1### \2'),
            
            # 二级标题: # 1.1. 标题  
            (r'^(\s*)#\s+(\d+\.\d+\.\s+.*)$', r'\1## \2'),
            
            # 一级标题: # 1. 标题
            (r'^(\s*)#\s+(\d+\.\s+.*)$', r'\1# \2'),
            
            # 无编号一级标题: # Abstract, # Conclusion 等
            (r'^(\s*)#\s+(' + '|'.join(self.unnumbered_h1_keywords) + r')(\s*.*)$', r'\1# \2\3'),
        ]
    
    def normalize_headings(self, markdown_text: str) -> List[str]:
        """
        对学术论文的Markdown文本进行标题层级规范化，并返回所有1级标题列表
        
        将PDF解析工具错误标记的所有一级标题(#)根据编号模式恢复为正确的标题层级
        
        Args:
            markdown_text: 包含论文内容的完整Markdown文本字符串
        
        Returns:
            List[str]: 所有1级标题列表
        """
        
        # 按行分割文本
        lines = markdown_text.split('\n')
        normalized_lines = []
        h1_headings = []  # 存储真正的1级标题
        
        # 统计信息
        stats = {
            'h1_numbered': 0,      # 编号一级标题
            'h1_unnumbered': 0,    # 无编号一级标题  
            'h2': 0,              # 二级标题
            'h3': 0,              # 三级标题
            'unchanged': 0        # 未匹配的标题
        }
        
        for i, line in enumerate(lines):
            original_line = line
            processed = False
            
            # 检查是否是以#开头的标题行
            if re.match(r'^\s*#\s+', line):
                # 按优先级尝试匹配各种模式
                for pattern, replacement in self.patterns:
                    if re.match(pattern, line):
                        # 执行替换
                        new_line = re.sub(pattern, replacement, line)
                        normalized_lines.append(new_line)
                        
                        # 统计处理结果并收集1级标题
                        if '###' in new_line:
                            stats['h3'] += 1
                        elif '##' in new_line:
                            stats['h2'] += 1
                        elif '# ' in new_line and not re.match(r'^\s*##', new_line):
                            # 只有真正的1级标题才收集
                            if re.match(r'^\s*#\s+\d+\.', new_line):
                                # 编号的一级标题 (如 # 1. Introduction)
                                stats['h1_numbered'] += 1
                                h1_headings.append(new_line.strip())
                            elif self._is_unnumbered_h1(new_line):
                                # 无编号的一级标题 (如 # Abstract, # Conclusion)
                                stats['h1_unnumbered'] += 1
                                h1_headings.append(new_line.strip())
                        
                        processed = True
                        break
                
                # 如果没有匹配任何模式，检查是否为无编号的1级标题
                if not processed:
                    normalized_lines.append(line)
                    if self._is_unnumbered_h1(line):
                        stats['h1_unnumbered'] += 1
                        h1_headings.append(line.strip())
                    else:
                        stats['unchanged'] += 1
            else:
                # 非标题行，直接添加
                normalized_lines.append(line)
        
        return h1_headings
    
    def _is_unnumbered_h1(self, line: str) -> bool:
        """
        判断是否为1级标题
        
        规则：
        1. 所有以#开头的都是标题
        2. 通过序号格式判断级别：
           - 1, 1. → 1级标题
           - 1.1, 1.1. → 2级标题
           - 1.1.1, 1.1.1. → 3级标题
        3. 没有序号的标题默认为1级标题
        
        Args:
            line: 标题行
        
        Returns:
            bool: 是否为1级标题
        """
        # 提取标题文本（去掉#和空格）
        title_text = re.sub(r'^\s*#+\s*', '', line).strip()
        
        # 1. 检查是否匹配已知的无编号1级标题关键词（精确匹配）
        for keyword in self.unnumbered_h1_keywords:
            if title_text.lower() == keyword.lower():
                return True
        
        # 2. 检查序号格式来判断标题级别
        # 2.1 匹配1级标题格式：纯数字开头（如 "1", "1.", "2", "2."）
        if re.match(r'^\d+\.?\s+', title_text):
            # 检查是否包含小数点（如 1.1, 1.1.1）
            if not re.search(r'\d+\.\d+', title_text):
                return True  # 这是1级标题
        
        # 2.2 检查是否为2级或3级标题格式
        if re.search(r'\d+\.\d+', title_text):
            return False  # 这是2级或3级标题
        
        # 3. 没有序号的标题默认为1级标题
        return True


    def extract_headings_only(self, markdown_text: str) -> List[str]:
        """
        提取规范化后的所有标题行
        
        Args:
            markdown_text: Markdown文本
        
        Returns:
            List[str]: 所有标题行的列表
        """
        lines = markdown_text.split('\n')
        headings = []
        
        for line in lines:
            if re.match(r'^\s*#+\s+', line):
                headings.append(line.strip())
        
        return headings
    
    def extract_h1_headings(self, markdown_text: str) -> List[str]:
        """
        提取所有1级标题，按在文档中出现的顺序返回
        
        Args:
            markdown_text: Markdown文本
        
        Returns:
            List[str]: 1级标题行的列表，每个元素是完整的原始行字符串（包含#号）
        """
        lines = markdown_text.split('\n')
        h1_headings = []
        
        for line in lines:
            line = line.strip()
            # 检查是否为标题行
            if line.startswith('#'):
                # 检查是否为1级标题
                if self._is_unnumbered_h1(line):
                    h1_headings.append(line)  # 返回完整的原始行（包含#号）
        
        return h1_headings

    def analyze_heading_structure(self, markdown_text: str) -> dict:
        """
        分析标题结构，返回层级统计信息
        
        Args:
            markdown_text: Markdown文本
        
        Returns:
            dict: 标题结构分析结果
        """
        headings = self.extract_headings_only(markdown_text)
        
        structure = {
            'total_headings': len(headings),
            'h1_count': 0,
            'h2_count': 0, 
            'h3_count': 0,
            'h4_count': 0,
            'h5_count': 0,
            'h6_count': 0,
            'headings_by_level': {}
        }
        
        for heading in headings:
            # 计算标题层级
            level = len(re.match(r'^#+', heading).group())
            structure[f'h{level}_count'] += 1
            
            if level not in structure['headings_by_level']:
                structure['headings_by_level'][level] = []
            structure['headings_by_level'][level].append(heading)
        
        return structure

    def process_markdown_file(self, file_path: str) -> List[str]:
        """
        处理实际的Markdown文件
        
        Args:
            file_path: Markdown文件路径
        
        Returns:
            List[str]: 所有1级标题列表
        """
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 规范化处理，返回1级标题列表
            h1_headings = self.normalize_headings(content)
            
            return h1_headings
            
        except FileNotFoundError:
            return []
        except Exception as e:
            return []

    def process_markdown_content(self, markdown_content: str) -> List[str]:
        """
        处理Markdown内容字符串（不依赖文件）
        
        Args:
            markdown_content: Markdown内容字符串
        
        Returns:
            List[str]: 所有1级标题列表
        """
        try:
            # 规范化处理，返回1级标题列表
            h1_headings = self.normalize_headings(markdown_content)
            return h1_headings
        except Exception as e:
            print(f"处理Markdown内容时发生错误: {e}")
            return []

# 运行测试
if __name__ == "__main__":
    # 创建规范化器实例
    normalizer = HeadingNormalizer()
    
    # 测试用例1: 模拟PDF解析后的错误标题格式
    test_text_1 = """# Abstract
This is the abstract content.

# 1. Introduction
This is the introduction.

# 1.1 Background
Background information here.

# 1.1.1 Historical Context
Historical context details.

# 1.2 Related Work
Related work section.

# 1.2.1 Previous Studies
Previous studies details.

# 2. Methodology
Methodology section.

# 2.1 Data Collection
Data collection methods.

# 2.1.1 Sampling Strategy
Sampling strategy details.

# 3. Results
Results section.

# Conclusion
This is the conclusion.

# References
References list."""
    
    # 规范化处理，返回1级标题列表
    h1_headings = normalizer.normalize_headings(test_text_1)
    print("1级标题列表:", h1_headings)
    
    # 分析标题结构
    structure = normalizer.analyze_heading_structure(test_text_1)
    print("标题结构分析:", structure)
    
    # 可选：处理实际文件
    test_files = [
         "/Users/xiaokong/task/2025/paper_vis/vis/md/3791465d4e18e4033b5c7bd322c44df2.md",
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            h1_headings = normalizer.process_markdown_file(file_path)
            print(f"文件 {file_path} 的1级标题:", h1_headings)
