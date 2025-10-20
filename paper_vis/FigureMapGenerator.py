#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合图表映射生成器
整合内容提取、数据合并和图表文本匹配功能，生成按泳道组织的图表映射

功能流程：
1. 使用ComprehensiveContentExtractor获取按泳道组织的原始文本内容
2. 使用merge_data.py合并content_list.json和middle.json
3. 使用FigureTextMatchingPipeline进行图表文本匹配
4. 根据figure_caption在各泳道原始文本中的存在情况判断图表所属泳道
5. 生成最终的figure_map字典

核心逻辑：
- 只有原文中实际存在的图表才会被归类到相应泳道
- 使用严格完整匹配：清理后的figure_caption必须在某个泳道的原始文本中完整出现
- 如果图表标题在多个泳道中都出现，选择第一个匹配的泳道
- 不是所有图表都会被划分，取决于原文中是否提及
"""

import os
import json
import glob
import re
from typing import Dict, List, Optional
from ComprehensiveContentExtractor import ComprehensiveContentExtractor
from merge_data import DataMerger
from FigureTextMatchingPipeline import FigureTextMatchingPipeline


class FigureMapGenerator:
    """综合图表映射生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.content_extractor = ComprehensiveContentExtractor()
        self.data_merger = DataMerger()
        self.figure_pipeline = FigureTextMatchingPipeline()
    
    def generate_figure_map(self, content_list: List[Dict], middle_data: Dict, figure_dict: Dict[str, str], content_by_lane: Dict[str, str]) -> Dict[str, List[Dict]]:
        """
        生成综合图表映射
        
        Args:
            content_list: content_list数据
            middle_data: middle数据
            figure_dict: 图表字典 {file_name: base64_data}
            content_by_lane: 按泳道组织的内容
        
        Returns:
            Dict[str, List[Dict]]: 按泳道组织的图表映射字典
        """
        try:
            print(f"=== 开始处理图表映射 ===")
            
            # 步骤1: 合并数据
            print("步骤1: 合并content_list和middle数据...")
            print(f"调试: content_list前3项类型: {[type(item) for item in content_list[:3]]}")
            merged_data = self.data_merger.merge_data(content_list, middle_data)
            
            print(f"数据合并完成，共 {len(merged_data)} 条记录")
            print()
            
            # 步骤2: 图表文本匹配
            print("步骤2: 进行图表文本匹配...")
            matching_result = self.figure_pipeline.process_merged_document(
                merged_data, figure_dict, "document_id"
            )
            
            print("图表匹配完成")
            print()
            
            # 步骤3: 根据figure_caption在原始文本中的存在情况判断泳道并生成最终映射
            print("步骤3: 生成最终图表映射...")
            figure_map = self._generate_final_figure_map(matching_result, content_by_lane, figure_dict)
            
            print("=== 图表映射生成完成 ===")
            return figure_map
            
        except Exception as e:
            print(f"生成图表映射过程中发生异常: {e}")
            return {}
    
    
    def _generate_final_figure_map(self, matching_result: Dict, content_by_lane: Dict[str, str], figure_dict: Dict[str, str]) -> Dict[str, List[Dict]]:
        """
        生成最终的图表映射
        
        Args:
            matching_result: 图表匹配结果
            content_by_lane: 按泳道组织的内容
            figure_dict: 图表字典 {file_name: base64_data}
        
        Returns:
            Dict[str, List[Dict]]: 最终的图表映射字典
        """
        figure_map = {
            'Context & Related Work': [],
            'Methodology & Setup': [],
            'Results & Analysis': [],
            'Conclusion': []
        }
        
        if 'results' not in matching_result:
            print("错误: 匹配结果中缺少results字段")
            return figure_map
        
        for figure_info in matching_result['results']:
            figure_caption = figure_info.get('figure_caption', '')
            figure_id = figure_info.get('figure_id', '')
            matches = figure_info.get('matches', [])
            
            # 根据figure_caption和figure_id判断所属泳道
            assigned_lane = self._determine_figure_lane(figure_caption, figure_id, content_by_lane)
            
            if assigned_lane:
                # 提取reference_text列表
                reference_texts = [match.get('reference_text', '') for match in matches]
                
                # 构建图表信息
                # 从figure_dict中获取对应的base64数据
                figure_base64 = figure_dict.get(figure_id, '')
                
                figure_data = {
                    'figure_id': figure_id,
                    'figure_caption': figure_caption,
                    'reference_text': reference_texts,
                    'figure_base64': figure_base64
                }
                
                figure_map[assigned_lane].append(figure_data)
                print(f"图表 {figure_id} 分配到泳道: {assigned_lane}")
            else:
                print(f"警告: 无法确定图表 {figure_id} 的泳道归属")
        
        # 打印统计信息
        print("\n=== 图表映射统计 ===")
        for lane, figures in figure_map.items():
            print(f"{lane}: {len(figures)} 个图表")
        
        return figure_map
    
    def _determine_figure_lane(self, figure_caption: str, figure_id: str, content_by_lane: Dict[str, str]) -> Optional[str]:
        """
        根据figure_caption和figure_id在原始文本中的存在情况确定图表所属的泳道
        使用严格完整匹配：只有清理后的标题在某个泳道中完整出现时才归类
        
        Args:
            figure_caption: 图表标题
            figure_id: 图表ID（文件名）
            content_by_lane: 按泳道组织的原始文本内容
        
        Returns:
            str: 泳道名称，如果无法确定返回None
        """
        if not figure_caption:
            return None
        
        # 清理figure_caption，提取核心内容
        caption_clean = self._clean_figure_caption(figure_caption)
        
        # 在每个泳道的原始文本中搜索figure_caption
        for lane_name, lane_content in content_by_lane.items():
            if not lane_content:
                continue
            
            # 检查figure_caption是否在该泳道的原始文本中出现
            if self._is_caption_in_content(caption_clean, lane_content):
                print(f"   ✓ 在泳道 '{lane_name}' 中找到图表标题")
                return lane_name
        
        # 如果标题匹配失败，尝试根据figure_id（文件名）匹配
        print(f"   🔄 尝试根据文件名匹配: {figure_id}")
        for lane_name, lane_content in content_by_lane.items():
            if not lane_content:
                continue
            
            # 检查文件名是否在该泳道的原始文本中出现
            if figure_id.lower() in lane_content.lower():
                print(f"   ✓ 在泳道 '{lane_name}' 中找到文件名")
                return lane_name
        
        # 如果文件名匹配也失败，尝试根据图表编号匹配
        print(f"   🔄 尝试根据图表编号匹配")
        import re
        number_match = re.search(r'(\d+)', figure_id)
        if number_match:
            figure_number = number_match.group(1)
            for lane_name, lane_content in content_by_lane.items():
                if not lane_content:
                    continue
                
                # 检查图表编号是否在该泳道的原始文本中出现
                if f"figure {figure_number}" in lane_content.lower() or f"table {figure_number}" in lane_content.lower():
                    print(f"   ✓ 在泳道 '{lane_name}' 中找到图表编号 {figure_number}")
                    return lane_name
        
        print(f"   ⚠️ 未在任何泳道的原始文本中找到图表标题或文件名")
        return None
    
    def _clean_figure_caption(self, caption: str) -> str:
        """
        清理图表标题，提取核心内容用于严格匹配
        
        Args:
            caption: 原始图表标题
        
        Returns:
            str: 清理后的标题
        """
        if not caption:
            return ""
        
        # 移除常见的图表编号前缀（如 "Figure 1:", "Fig. 2:", "Table 3." 等）
        caption = re.sub(r'^(Figure|Fig|Table|Tab)\s*\d+[:\-\.]?\s*', '', caption, flags=re.IGNORECASE)
        
        # 移除多余的空白字符，但保持原始格式
        caption = re.sub(r'\s+', ' ', caption).strip()
        
        return caption
    
    def _is_caption_in_content(self, caption: str, content: str) -> bool:
        """
        检查图表标题是否在内容中出现（严格完整匹配）
        
        Args:
            caption: 清理后的图表标题
            content: 泳道的原始文本内容
        
        Returns:
            bool: 是否找到匹配
        """
        if not caption or not content:
            return False
        
        # 严格匹配：检查清理后的标题是否在内容中完整出现
        return caption.lower() in content.lower()
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
        
        Returns:
            float: 相似度分数 (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # 简单的词汇重叠相似度计算
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0


def main():
    """主函数，用于测试图表映射生成功能"""
    print("=== 图表映射生成器测试 ===")
    
    # 创建生成器实例
    generator = FigureMapGenerator()
    
    # 测试文件夹路径（请根据实际情况修改）
    test_folder_path = "/Users/xiaokong/task/2025/paper_vis/vis/arxiv/4e787a2a-ca8f-41a4-afc9-89d0df4d224c"
    
    # 检查文件夹是否存在
    if not os.path.exists(test_folder_path):
        print(f"错误: 测试文件夹不存在: {test_folder_path}")
        print("请修改 test_folder_path 变量为实际存在的文件夹路径")
        return
    
    print(f"测试文件夹: {test_folder_path}")
    print()
    
    # 执行图表映射生成
    figure_map = generator.generate_figure_map(test_folder_path)
    # 将figure_map保存到json文件
    with open(os.path.join(test_folder_path, "figure_map.json"), "w", encoding="utf-8") as f:
        json.dump(figure_map, f, ensure_ascii=False, indent=2)
    
    if figure_map:
        print("=== 最终图表映射结果 ===")
        for lane_name, figures in figure_map.items():
            print(f"\n泳道: {lane_name}")
            print(f"图表数量: {len(figures)}")
            
            for i, figure in enumerate(figures, 1):
                print(f"  {i}. 图表ID: {figure['figure_id']}")
                print(f"     标题: {figure['figure_caption'][:100]}...")
                print(f"     引用数量: {len(figure['reference_text'])}")
                print()
    else:
        print("图表映射生成失败")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()
