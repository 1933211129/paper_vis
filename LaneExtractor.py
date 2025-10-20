#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
泳道抽取器
从PDF文件解析获取markdown内容，然后提取五大泳道的原始文本，并多进程并行调用五个抽取模块

功能流程：
1. 解析PDF文件获取markdown内容
2. 调用ComprehensiveContentExtractor.extract_comprehensive_content_from_string获取四个泳道的原始文本
3. 多进程并行调用五个抽取模块（ContextRelatedWork、MethodologySetup、ResultsAnalysis、Conclusion、InnovationDiscovery）
4. 返回JSON对象，不生成磁盘文件

核心特性：
- 严格的多进程并行处理，五个抽取流程同时进行
- 处理PDF文件，不依赖md文件
- 返回JSON对象，不生成磁盘文件
- 五大泳道：传统四大泳道 + Innovation Discovery
"""

import os
import json
import multiprocessing
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import time

# 导入必要的模块
from pdf_parse import PDFParserClient
from ComprehensiveContentExtractor import ComprehensiveContentExtractor
from ContextRelatedWork import analyze_context_related_work_sync
from MethodologySetup import analyze_methodology_setup_sync
from ResultsAnalysis import analyze_results_analysis_sync
from Conclusion import analyze_conclusion_sync
from AbstractSteps import extract_text_for_llm
from InnovationDiscovery import analyze_innovation_discovery_sync


class LaneExtractor:
    """泳道抽取器 - 五大泳道版本"""
    
    def __init__(self):
        """初始化抽取器"""
        self.content_extractor = ComprehensiveContentExtractor()
        self.pdf_parser = PDFParserClient()
        
        # 五大抽取模块的映射
        self.extraction_modules = {
            'Context & Related Work': analyze_context_related_work_sync,
            'Methodology & Setup': analyze_methodology_setup_sync,
            'Results & Analysis': analyze_results_analysis_sync,
            'Conclusion': analyze_conclusion_sync,
            'Innovation Discovery': analyze_innovation_discovery_sync
        }
    
    def extract_lanes_from_pdf(self, pdf_path: str) -> Dict[str, List[Dict]]:
        """
        从PDF文件提取五大泳道的内容并返回JSON对象
        
        Args:
            pdf_path: PDF文件路径
        
        Returns:
            包含五大泳道抽取结果的字典
        """
        print("=== 五大泳道抽取器启动 ===")
        print(f"目标PDF文件: {pdf_path}")
        
        # 步骤1: 解析PDF文件获取markdown内容
        md_content = self._parse_pdf_to_markdown(pdf_path)
        if not md_content:
            print("❌ 未能从PDF文件中解析出markdown内容")
            return {}
        
        print(f"✅ PDF解析成功，markdown内容长度: {len(md_content)} 字符")
        
        # 步骤2: 提取四个传统泳道的原始文本内容
        lane_contents = self._extract_traditional_lane_contents(md_content)
        if not lane_contents:
            print("❌ 未能从markdown内容中提取到传统泳道内容")
            return {}
        
        # 步骤3: 准备 Innovation Discovery 所需的两段输入
        try:
            abstract_excerpt = extract_text_for_llm(md_content) or ""
        except Exception:
            abstract_excerpt = ""
        conclusion_text = lane_contents.get('Conclusion', '') or ""
        lane_contents['Innovation Discovery'] = json.dumps({
            'abstract_excerpt': abstract_excerpt,
            'conclusion_text': conclusion_text
        }, ensure_ascii=False)

        # 步骤4: 多进程并行抽取五大泳道
        print("开始多进程并行抽取五大泳道...")
        extraction_results = self._parallel_extract_lanes(lane_contents)
        
        print("=== 五大泳道抽取完成 ===")
        return extraction_results
    
    def extract_lanes_from_content(self, md_content: str) -> Dict[str, List[Dict]]:
        """
        从markdown内容提取五大泳道的内容并返回JSON对象（用于API模式）
        
        Args:
            md_content: markdown内容字符串
        
        Returns:
            包含五大泳道抽取结果的字典
        """
        print("=== 五大泳道抽取器启动（内容模式） ===")
        print(f"markdown内容长度: {len(md_content)} 字符")
        
        if not md_content:
            print("❌ 未能从PDF文件中解析出markdown内容")
            return {}
        
        print(f"✅ Markdown内容获取成功，长度: {len(md_content)} 字符")
        
        # 步骤1: 提取四个传统泳道的原始文本内容
        lane_contents = self._extract_traditional_lane_contents(md_content)
        if not lane_contents:
            print("❌ 未能从markdown内容中提取到传统泳道内容")
            return {}
        
        # 步骤2: 准备 Innovation Discovery 所需的两段输入
        try:
            abstract_excerpt = extract_text_for_llm(md_content) or ""
        except Exception:
            abstract_excerpt = ""
        conclusion_text = lane_contents.get('Conclusion', '') or ""
        lane_contents['Innovation Discovery'] = json.dumps({
            'abstract_excerpt': abstract_excerpt,
            'conclusion_text': conclusion_text
        }, ensure_ascii=False)

        # 步骤3: 多进程并行抽取五大泳道
        print("开始多进程并行抽取五大泳道...")
        extraction_results = self._parallel_extract_lanes(lane_contents)
        
        print("=== 五大泳道抽取完成（内容模式） ===")
        return extraction_results
    
    def _parse_pdf_to_markdown(self, pdf_path: str) -> Optional[str]:
        """
        解析PDF文件获取markdown内容
        
        Args:
            pdf_path: PDF文件路径
        
        Returns:
            markdown内容字符串，如果解析失败返回None
        """
        print("步骤1: 解析PDF文件...")
        print(f"  处理文件: {os.path.basename(pdf_path)}")
        
        try:
            # 调用PDF解析器
            pdf_result = self.pdf_parser.upload_pdf(pdf_path)
            
            if pdf_result and 'md_content' in pdf_result:
                md_content = pdf_result['md_content']
                print(f"  ✅ PDF解析成功")
                print(f"    - 文件名: {pdf_result.get('filename', 'N/A')}")
                print(f"    - 版本: {pdf_result.get('version', 'N/A')}")
                print(f"    - 后端: {pdf_result.get('backend', 'N/A')}")
                print(f"    - Markdown内容长度: {len(md_content)} 字符")
                return md_content
            else:
                print(f"  ❌ PDF解析结果中缺少md_content字段")
                return None
                
        except Exception as e:
            print(f"  ❌ PDF解析失败: {e}")
            return None
    
    def _extract_traditional_lane_contents(self, md_content: str) -> Dict[str, str]:
        """
        从markdown内容中提取四个传统泳道的原始文本内容
        
        Args:
            md_content: markdown内容字符串
        
        Returns:
            按泳道名称组织的原始文本内容字典
        """
        print("步骤2: 提取传统泳道原始文本内容...")
        
        try:
            # 调用ComprehensiveContentExtractor的字符串版本获取泳道内容
            lane_contents = self.content_extractor.extract_comprehensive_content_from_string(md_content)
            
            if lane_contents:
                for lane_name, content in lane_contents.items():
                    if content and content.strip():
                        print(f"    ✓ {lane_name}: {len(content)} 字符")
                    else:
                        print(f"    ⚠ {lane_name}: 内容为空")
                return lane_contents
            else:
                print(f"    ❌ 未能提取到任何传统泳道内容")
                return {}
                
        except Exception as e:
            print(f"    ❌ 处理markdown内容失败: {e}")
            return {}
    
    def _parallel_extract_lanes(self, lane_contents: Dict[str, str]) -> Dict[str, List[Dict]]:
        """
        多进程并行抽取五大泳道的内容
        
        Args:
            lane_contents: 按泳道名称组织的原始文本内容
        
        Returns:
            抽取结果字典
        """
        print("步骤3: 多进程并行抽取五大泳道...")
        
        # 准备任务参数
        tasks = []
        for lane_name, content in lane_contents.items():
            if content and content.strip():
                extraction_func = self.extraction_modules[lane_name]
                tasks.append((lane_name, extraction_func, content))
                print(f"  ✓ 准备任务: {lane_name}")
            else:
                print(f"  ⚠ 跳过空内容: {lane_name}")
        
        if not tasks:
            print("❌ 没有有效的抽取任务")
            return {}
        
        # 多进程并行执行
        extraction_results = {}
        start_time = time.time()
        
        with ProcessPoolExecutor(max_workers=5) as executor:
            # 提交所有任务
            future_to_lane = {}
            for lane_name, extraction_func, content in tasks:
                future = executor.submit(self._extract_single_lane, lane_name, extraction_func, content)
                future_to_lane[future] = lane_name
            
            # 收集结果
            completed_count = 0
            for future in as_completed(future_to_lane):
                lane_name = future_to_lane[future]
                try:
                    result = future.result()
                    extraction_results[lane_name] = result
                    completed_count += 1
                    print(f"  ✓ 完成 {lane_name} ({completed_count}/{len(tasks)})")
                except Exception as e:
                    print(f"  ❌ {lane_name} 抽取失败: {e}")
                    extraction_results[lane_name] = []
        
        end_time = time.time()
        print(f"多进程抽取完成，耗时: {end_time - start_time:.2f}秒")
        print()
        
        return extraction_results
    
    def _extract_single_lane(self, lane_name: str, extraction_func, content: str) -> List[Dict]:
        """
        抽取单个泳道的内容（用于多进程调用）
        
        Args:
            lane_name: 泳道名称
            extraction_func: 抽取函数
            content: 原始文本内容
        
        Returns:
            抽取结果列表
        """
        try:
            result = extraction_func(content)
            if result:
                return [result]  # 包装为列表以保持一致性
            else:
                return []
        except Exception as e:
            print(f"进程内错误 - {lane_name}: {e}")
            return []
    


def main():
    """主函数 - 测试五大泳道抽取器"""
    print("=== 五大泳道抽取器测试 ===")
    
    # 测试PDF文件路径
    test_pdf_path = "/Users/xiaokong/Desktop/1701.06538v1.pdf"
    
    # 检查PDF文件是否存在
    if not os.path.exists(test_pdf_path):
        print(f"❌ 测试PDF文件不存在: {test_pdf_path}")
        return
    
    # 创建抽取器
    extractor = LaneExtractor()
    
    # 执行五大泳道抽取
    results = extractor.extract_lanes_from_pdf(test_pdf_path)
    # 保存结果到文件
    
    if results:
        print("\n=== 五大泳道抽取结果摘要 ===")
        for lane_name, lane_results in results.items():
            print(f"\n🏊 {lane_name}: {len(lane_results)} 个结果")
            if lane_results:
                # 显示第一个结果的键
                first_result = lane_results[0]
                if isinstance(first_result, dict):
                    print(f"  关键字段: {list(first_result.keys())}")
                    # 显示部分内容预览
                    for key, value in first_result.items():
                        if isinstance(value, str) and len(value) > 100:
                            print(f"  {key}: {value[:100]}...")
                        else:
                            print(f"  {key}: {value}")
        with open("lane_extraction_result2222.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("\n=== 完整JSON结果 ===")
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("❌ 抽取失败，无结果")


if __name__ == "__main__":
    main()
