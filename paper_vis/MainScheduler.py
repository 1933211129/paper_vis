#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合主调度器 - 完整论文处理系统
从PDF文件到最终超大JSON对象的端到端处理

功能流程：
1. PDF解析：使用PDFParserClient解析PDF文件
2. 并行处理：AbstractSteps + LaneExtractor + FigureMapGenerator
3. 数据整合：生成包含所有信息的超大JSON对象

输入：PDF文件路径
输出：包含以下内容的超大JSON对象：
- metadata: 论文元数据（标题、作者）
- abstract: 摘要语步（4个步骤）
- lanes: 五大泳道内容
- figure_map: 图表映射
- processing_info: 处理信息

核心特性：
- 端到端处理，从PDF到最终JSON
- 智能并发处理，避免重复计算
- 完整的错误处理和状态监控
- 内存优化，避免重复数据存储
"""

import os
import json
import time
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import threading

# 导入必要的模块
from pdf_parse import PDFParserClient
from AbstractSteps import analyze_abstract_steps_from_content
from LaneExtractor import LaneExtractor
from FigureMapGenerator import FigureMapGenerator


class MainScheduler:
    """综合主调度器 - 完整论文处理系统"""
    
    def __init__(self):
        """初始化调度器"""
        self.pdf_parser = PDFParserClient()
        self.lane_extractor = LaneExtractor()
        self.figure_generator = FigureMapGenerator()
        
        # 处理状态跟踪
        self.processing_info = {
            'start_time': None,
            'end_time': None,
            'total_time': 0,
            'steps_completed': [],
            'errors': []
        }
    
    def process_uploaded_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        处理上传的PDF文件流，生成包含所有信息的超大JSON对象
        
        Args:
            file_content: PDF文件内容（字节流）
            filename: 文件名
        
        Returns:
            Dict[str, Any]: 包含所有处理结果的超大JSON对象
        """
        print("=" * 80)
        print("🚀 综合主调度器启动（上传文件模式）")
        print(f"📄 目标PDF文件: {filename}")
        print("=" * 80)
        
        self.processing_info['start_time'] = time.time()
        
        try:
            # 步骤1: PDF解析（直接使用文件内容）
            print("\n📋 步骤1: PDF文件解析（上传模式）")
            pdf_result = self._parse_uploaded_pdf(file_content, filename)
            if not pdf_result:
                return self._create_error_result("PDF解析失败")
            
            # 步骤2: 并行处理所有任务
            print("\n⚡ 步骤2: 并行处理所有任务")
            parallel_results = self._execute_parallel_processing(pdf_result)
            if not parallel_results['success']:
                return self._create_error_result(f"并行处理失败: {parallel_results['error']}")
            
            # 步骤3: 生成最终超大JSON对象
            print("\n🎯 步骤3: 生成最终超大JSON对象")
            final_result = self._generate_final_json(pdf_result, parallel_results)
            
            self.processing_info['end_time'] = time.time()
            self.processing_info['total_time'] = self.processing_info['end_time'] - self.processing_info['start_time']
            
            print("=" * 80)
            print("🎉 综合处理完成")
            print(f"⏱️ 总耗时: {self.processing_info['total_time']:.2f}秒")
            print(f"📊 处理步骤: {len(self.processing_info['steps_completed'])}")
            print("=" * 80)
            
            return final_result
            
        except Exception as e:
            self.processing_info['errors'].append(str(e))
            print(f"❌ 综合处理失败: {e}")
            return self._create_error_result(f"处理异常: {e}")

    def process_pdf_file(self, pdf_path: str) -> Dict[str, Any]:
        """
        处理PDF文件，生成包含所有信息的超大JSON对象
        
        Args:
            pdf_path: PDF文件路径
        
        Returns:
            Dict[str, Any]: 包含所有处理结果的超大JSON对象
        """
        print("=" * 80)
        print("🚀 综合主调度器启动")
        print(f"📄 目标PDF文件: {pdf_path}")
        print("=" * 80)
        
        self.processing_info['start_time'] = time.time()
        
        try:
            # 步骤1: PDF解析
            print("\n📋 步骤1: PDF文件解析")
            pdf_result = self._parse_pdf_file(pdf_path)
            if not pdf_result:
                return self._create_error_result("PDF解析失败")
            
            # 步骤2: 并行处理所有任务
            print("\n⚡ 步骤2: 并行处理所有任务")
            parallel_results = self._execute_parallel_processing(pdf_result)
            if not parallel_results['success']:
                return self._create_error_result(f"并行处理失败: {parallel_results['error']}")
            
            # 步骤3: 生成最终超大JSON对象
            print("\n🎯 步骤3: 生成最终超大JSON对象")
            final_result = self._generate_final_json(pdf_result, parallel_results)
            
            self.processing_info['end_time'] = time.time()
            self.processing_info['total_time'] = self.processing_info['end_time'] - self.processing_info['start_time']
            
            print("=" * 80)
            print("🎉 综合处理完成")
            print(f"⏱️ 总耗时: {self.processing_info['total_time']:.2f}秒")
            print(f"📊 处理步骤: {len(self.processing_info['steps_completed'])}")
            print("=" * 80)
            
            return final_result
            
        except Exception as e:
            self.processing_info['errors'].append(str(e))
            print(f"❌ 综合处理失败: {e}")
            return self._create_error_result(f"处理异常: {e}")
    
    def _parse_uploaded_pdf(self, file_content: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """
        解析上传的PDF文件流
        
        Args:
            file_content: PDF文件内容（字节流）
            filename: 文件名
        
        Returns:
            Dict[str, Any]: PDF解析结果，包含md_content, middle_json, content_list, figure_dict
        """
        try:
            print(f"📄 开始解析上传的PDF文件: {filename}")
            
            # 使用PDFParserClient解析上传的PDF文件
            # 需要修改PDFParserClient来支持文件流
            pdf_result = self.pdf_parser.upload_pdf_from_content(file_content, filename)
            
            if not pdf_result:
                print("❌ PDF解析失败")
                return None
            
            # 提取关键字段
            md_content = pdf_result.get('md_content', '')
            middle_json_str = pdf_result.get('middle_json', '{}')
            content_list_str = pdf_result.get('content_list', '[]')
            figure_dict = pdf_result.get('figure_dict', {})
            
            print(f"✅ PDF解析完成")
            print(f"   - Markdown内容长度: {len(md_content)} 字符")
            print(f"   - Middle JSON长度: {len(middle_json_str)} 字符")
            print(f"   - Content List长度: {len(content_list_str)} 字符")
            print(f"   - 图表数量: {len(figure_dict)}")
            
            # 解析JSON数据
            try:
                middle_data = json.loads(middle_json_str)
                content_list = json.loads(content_list_str)
                print(f"✅ JSON解析完成")
                print(f"   - Middle数据页数: {len(middle_data.get('pdf_info', []))}")
                print(f"   - Content List记录数: {len(content_list)}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                return None
            
            self.processing_info['steps_completed'].append('pdf_parsing')
            
            return {
                'md_content': md_content,
                'middle_data': middle_data,
                'content_list': content_list,
                'figure_dict': figure_dict,
                'pdf_path': filename,  # 使用文件名作为标识
                'pdf_info': {
                    'filename': pdf_result.get('filename', filename),
                    'version': pdf_result.get('version', ''),
                    'backend': pdf_result.get('backend', '')
                }
            }
            
        except Exception as e:
            print(f"❌ PDF解析异常: {e}")
            self.processing_info['errors'].append(f"PDF解析异常: {e}")
            return None

    def _parse_pdf_file(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        解析PDF文件
        
        Args:
            pdf_path: PDF文件路径
        
        Returns:
            Dict[str, Any]: PDF解析结果，包含md_content, middle_json, content_list, figure_dict
        """
        try:
            print(f"📄 开始解析PDF文件: {os.path.basename(pdf_path)}")
            
            # 使用PDFParserClient解析PDF
            pdf_result = self.pdf_parser.upload_pdf(pdf_path)
            
            if not pdf_result:
                print("❌ PDF解析失败")
                return None
            
            # 提取关键字段
            md_content = pdf_result.get('md_content', '')
            middle_json_str = pdf_result.get('middle_json', '{}')
            content_list_str = pdf_result.get('content_list', '[]')
            figure_dict = pdf_result.get('figure_dict', {})
            
            print(f"✅ PDF解析完成")
            print(f"   - Markdown内容长度: {len(md_content)} 字符")
            print(f"   - Middle JSON长度: {len(middle_json_str)} 字符")
            print(f"   - Content List长度: {len(content_list_str)} 字符")
            print(f"   - 图表数量: {len(figure_dict)}")
            
            # 解析JSON数据
            try:
                middle_data = json.loads(middle_json_str)
                content_list = json.loads(content_list_str)
                print(f"✅ JSON解析完成")
                print(f"   - Middle数据页数: {len(middle_data.get('pdf_info', []))}")
                print(f"   - Content List记录数: {len(content_list)}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                return None
            
            self.processing_info['steps_completed'].append('pdf_parsing')
            
            return {
                'md_content': md_content,
                'middle_data': middle_data,
                'content_list': content_list,
                'figure_dict': figure_dict,
                'pdf_path': pdf_path,  # 添加PDF路径，供LaneExtractor使用
                'pdf_info': {
                    'filename': pdf_result.get('filename', ''),
                    'version': pdf_result.get('version', ''),
                    'backend': pdf_result.get('backend', '')
                }
            }
            
        except Exception as e:
            print(f"❌ PDF解析异常: {e}")
            self.processing_info['errors'].append(f"PDF解析异常: {e}")
            return None
    
    def _execute_parallel_processing(self, pdf_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        并行执行所有处理任务
        
        Args:
            pdf_result: PDF解析结果
        
        Returns:
            Dict[str, Any]: 并行处理结果
        """
        print("🔄 启动线程池并行执行所有任务...")
        
        results = {
            'success': False,
            'abstract_result': None,
            'lane_result': None,
            'figure_map_result': None,
            'error': None
        }
        
        try:
            # 使用线程池并行执行三个主要任务
            with ThreadPoolExecutor(max_workers=3) as executor:
                # 提交任务
                abstract_future = executor.submit(
                    self._execute_abstract_steps, pdf_result['md_content']
                )
                lane_future = executor.submit(
                    self._execute_lane_extraction, pdf_result
                )
                figure_map_future = executor.submit(
                    self._execute_figure_mapping, pdf_result
                )
                
                # 收集结果
                abstract_result = abstract_future.result()
                lane_result = lane_future.result()
                figure_map_result = figure_map_future.result()
                
                results['abstract_result'] = abstract_result
                results['lane_result'] = lane_result
                results['figure_map_result'] = figure_map_result
                
                # 检查所有任务是否成功
                success_count = sum([
                    1 if abstract_result else 0,
                    1 if lane_result else 0,
                    1 if figure_map_result else 0
                ])
                
                results['success'] = success_count >= 2  # 至少2个任务成功
                
                if not results['success']:
                    failed_tasks = []
                    if not abstract_result:
                        failed_tasks.append("AbstractSteps")
                    if not lane_result:
                        failed_tasks.append("LaneExtraction")
                    if not figure_map_result:
                        failed_tasks.append("FigureMapping")
                    results['error'] = f"任务执行失败: {', '.join(failed_tasks)}"
                
        except Exception as e:
            results['error'] = f"并行执行异常: {e}"
            print(f"❌ 并行执行失败: {e}")
            self.processing_info['errors'].append(f"并行执行异常: {e}")
        
        return results
    
    def _execute_abstract_steps(self, md_content: str) -> Optional[Dict[str, Any]]:
        """
        执行AbstractSteps分析
        
        Args:
            md_content: markdown内容
        
        Returns:
            Dict[str, Any]: 分析结果，包含metadata和abstract
        """
        try:
            print("📝 开始执行AbstractSteps分析...")
            
            # 使用analyze_abstract_steps_from_content进行分析
            result = analyze_abstract_steps_from_content(md_content)
            
            if result:
                print("✅ AbstractSteps分析成功")
                print(f"   - 标题: {result.get('metadata', {}).get('title', 'N/A')}")
                print(f"   - 作者数量: {len(result.get('metadata', {}).get('authors', []))}")
                print(f"   - 摘要语步: {len(result.get('abstract', {}))}")
                self.processing_info['steps_completed'].append('abstract_analysis')
                return result
            else:
                print("❌ AbstractSteps分析失败")
                return None
                
        except Exception as e:
            print(f"❌ AbstractSteps分析异常: {e}")
            self.processing_info['errors'].append(f"AbstractSteps分析异常: {e}")
            return None
    
    def _execute_lane_extraction(self, pdf_result: Dict[str, Any]) -> Optional[Dict[str, List[Dict]]]:
        """
        执行泳道内容提取
        
        Args:
            pdf_result: PDF解析结果，包含md_content等字段
        
        Returns:
            Dict[str, List[Dict]]: 五大泳道抽取结果
        """
        try:
            print("🏊 开始执行泳道内容提取...")
            
            # 从PDF结果中获取markdown内容
            md_content = pdf_result.get('md_content', '')
            if not md_content:
                print("❌ 未能从PDF文件中解析出markdown内容")
                return None
            
            # 使用LaneExtractor进行完整的五大泳道抽取（基于内容）
            lane_result = self.lane_extractor.extract_lanes_from_content(md_content)
            
            if lane_result:
                print("✅ 泳道内容提取成功")
                for lane_name, lane_results in lane_result.items():
                    print(f"   - {lane_name}: {len(lane_results)} 个结果")
                self.processing_info['steps_completed'].append('lane_extraction')
                return lane_result
            else:
                print("❌ 泳道内容提取失败")
                return None
                
        except Exception as e:
            print(f"❌ 泳道内容提取异常: {e}")
            self.processing_info['errors'].append(f"泳道内容提取异常: {e}")
            return None
    
    def _execute_figure_mapping(self, pdf_result: Dict[str, Any]) -> Optional[Dict[str, List[Dict[str, Any]]]]:
        """
        执行图表映射生成
        
        Args:
            pdf_result: PDF解析结果
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: 图表映射结果
        """
        try:
            print("🗺️ 开始执行图表映射生成...")
            
            # 首先需要获取泳道内容，因为FigureMapGenerator需要它
            md_content = pdf_result['md_content']
            from ComprehensiveContentExtractor import ComprehensiveContentExtractor
            content_extractor = ComprehensiveContentExtractor()
            lane_content = content_extractor.extract_comprehensive_content_from_string(md_content)
            
            if not lane_content:
                print("❌ 无法获取泳道内容，图表映射失败")
                return None
            
            # 使用FigureMapGenerator生成图表映射
            figure_map = self.figure_generator.generate_figure_map(
                pdf_result['content_list'],
                pdf_result['middle_data'],
                pdf_result['figure_dict'],
                lane_content
            )
            
            if figure_map:
                print("✅ 图表映射生成成功")
                total_figures = sum(len(figures) for figures in figure_map.values())
                print(f"   - 总图表数: {total_figures}")
                for lane_name, figures in figure_map.items():
                    print(f"   - {lane_name}: {len(figures)} 个图表")
                self.processing_info['steps_completed'].append('figure_mapping')
                return figure_map
            else:
                print("❌ 图表映射生成失败")
                return None
                
        except Exception as e:
            print(f"❌ 图表映射生成异常: {e}")
            self.processing_info['errors'].append(f"图表映射生成异常: {e}")
            return None
    
    def _generate_final_json(self, pdf_result: Dict[str, Any], parallel_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成最终的超大JSON对象
        
        Args:
            pdf_result: PDF解析结果
            parallel_results: 并行处理结果
        
        Returns:
            Dict[str, Any]: 最终的超大JSON对象
        """
        try:
            print("🎯 开始生成最终超大JSON对象...")
            
            # 构建最终的超大JSON对象
            final_result = {
                # 论文元数据
                'metadata': parallel_results.get('abstract_result', {}).get('metadata', {
                    'title': '',
                    'authors': []
                }),
                
                # 摘要语步
                'abstract': parallel_results.get('abstract_result', {}).get('abstract', {
                    'Background/Problem': '',
                    'Method/Approach': '',
                    'Result': '',
                    'Conclusion/Contribution': ''
                }),
                
                # 五大泳道内容
                'lanes': parallel_results.get('lane_result', {}),
                
                # 图表映射
                'figure_map': parallel_results.get('figure_map_result', {}),
                
                # PDF信息
                'pdf_info': pdf_result.get('pdf_info', {}),
                
                # 处理信息
                'processing_info': {
                    'total_time': self.processing_info['total_time'],
                    'steps_completed': self.processing_info['steps_completed'],
                    'errors': self.processing_info['errors'],
                    'success': len(self.processing_info['errors']) == 0
                },
                
                # 原始数据（可选，用于调试）
                'raw_data': {
                    'md_content_length': len(pdf_result.get('md_content', '')),
                    'content_list_count': len(pdf_result.get('content_list', [])),
                    'figure_count': len(pdf_result.get('figure_dict', {}))
                }
            }
            
            print("✅ 最终超大JSON对象生成成功")
            print(f"   - 元数据: {'✅' if final_result['metadata']['title'] else '❌'}")
            print(f"   - 摘要语步: {'✅' if final_result['abstract'] else '❌'}")
            print(f"   - 泳道内容: {'✅' if final_result['lanes'] else '❌'}")
            print(f"   - 图表映射: {'✅' if final_result['figure_map'] else '❌'}")
            
            self.processing_info['steps_completed'].append('final_json_generation')
            
            # 添加成功状态
            final_result['success'] = True
            final_result['total_time'] = self.processing_info['total_time']
            
            return final_result
            
        except Exception as e:
            print(f"❌ 最终JSON生成异常: {e}")
            self.processing_info['errors'].append(f"最终JSON生成异常: {e}")
            return self._create_error_result(f"最终JSON生成异常: {e}")
    
    def _create_error_result(self, error_message: str, total_time: float = 0.0) -> Dict[str, Any]:
        """
        创建错误结果
        
        Args:
            error_message: 错误消息
            total_time: 总耗时
        
        Returns:
            Dict[str, Any]: 错误结果
        """
        return {
            'success': False,
            'error': error_message,
            'total_time': total_time,
            'processing_info': {
                'total_time': total_time,
                'steps_completed': self.processing_info['steps_completed'],
                'errors': self.processing_info['errors'] + [error_message],
                'success': False
            }
        }


def main():
    """主函数 - 测试综合主调度器"""
    print("=== 综合主调度器测试 ===")
    
    # 测试PDF文件路径（请根据实际情况修改）
    test_pdf_path = "/Users/xiaokong/Desktop/1701.06538v1.pdf"
    
    # 检查PDF文件是否存在
    if not os.path.exists(test_pdf_path):
        print(f"❌ 测试PDF文件不存在: {test_pdf_path}")
        print("请确保PDF文件路径正确")
        return
    
    # 创建调度器
    scheduler = MainScheduler()
    
    # 执行处理
    print(f"🚀 开始处理PDF文件: {os.path.basename(test_pdf_path)}")
    results = scheduler.process_pdf_file(test_pdf_path)
    
    if results.get('success', False):
        print("\n🎉 综合处理成功!")
        print(f"⏱️ 总耗时: {results.get('total_time', 0):.2f}秒")
        
        # 显示处理结果统计
        processing_info = results.get('processing_info', {})
        print(f"📊 处理步骤: {len(processing_info.get('steps_completed', []))}")
        print(f"✅ 成功步骤: {processing_info.get('steps_completed', [])}")
        
        if processing_info.get('errors'):
            print(f"⚠️ 错误信息: {processing_info.get('errors')}")
        
        # 显示数据统计
        print(f"\n📈 数据统计:")
        print(f"   - 论文标题: {results.get('metadata', {}).get('title', 'N/A')}")
        print(f"   - 作者数量: {len(results.get('metadata', {}).get('authors', []))}")
        print(f"   - 泳道数量: {len(results.get('lanes', {}))}")
        print(f"   - 图表总数: {sum(len(figures) for figures in results.get('figure_map', {}).values())}")
        
        # 保存结果到文件
        output_file = "222comprehensive_processing_result.json"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 完整结果已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存结果文件失败: {e}")
        
    else:
        print(f"\n❌ 综合处理失败: {results.get('error', '未知错误')}")
        processing_info = results.get('processing_info', {})
        if processing_info.get('errors'):
            print(f"错误详情: {processing_info.get('errors')}")


if __name__ == "__main__":
    main()
