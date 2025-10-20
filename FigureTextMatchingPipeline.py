from typing import List, Dict, Optional
from FigureReferenceExtractor import FigureReferenceExtractor
from EnhancementModules import EnhancementModules

class FigureTextMatchingPipeline:
    def __init__(self):
        self.extractor = FigureReferenceExtractor()
    
    def process_merged_document(self, merged_data: List[Dict], figure_dict: Dict[str, str], document_id: str = None) -> Dict:
        """处理合并后的文档数据，进行图表文本匹配"""
        print("开始图表匹配处理...")
        print(f"调试: merged_data前3项类型: {[type(item) for item in merged_data[:3]]}")
        
        # 1. 从merged_data中提取图表信息（使用image_caption和table_caption字段）
        figures = self._extract_figures_from_merged_data(merged_data)
        print(f"发现内容:\n  - 图片: {sum(1 for f in figures if f.get('type') == 'image')} 个")
        print(f"  - 表格: {sum(1 for f in figures if f.get('type') == 'table')} 个")
        print(f"  - 总计: {len(figures)} 个")
        
        # 2. 从merged_data中提取引用（保留位置信息）
        references = self._extract_references_from_merged_data(merged_data)
        print(f"提取到 {len(references)} 个引用")
        
        
        # 3. 为每个图表进行匹配
        results = []
        for fig in figures:
            figure_matches = self._match_figure_with_references(fig, references)
            results.append({
                'figure_id': fig['figure_id'],
                'figure_caption': fig['caption'],
                'figure_type': fig['type'],
                'page_idx': fig['page_idx'],
                'matches': figure_matches
            })
        
        return self._format_output(results, document_id)
    
    def _extract_figures_from_dict(self, figure_dict: Dict[str, str]) -> List[Dict]:
        """从figure_dict中提取图表信息"""
        figures = []
        
        for file_name, base64_data in figure_dict.items():
            # 根据文件名判断图表类型
            if 'figure' in file_name.lower() or 'fig' in file_name.lower():
                figure_type = 'image'
            elif 'table' in file_name.lower() or 'tab' in file_name.lower():
                figure_type = 'table'
            else:
                # 默认根据文件扩展名判断
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    figure_type = 'image'
                else:
                    figure_type = 'table'  # 默认作为表格处理
            
            # 从文件名提取编号
            import re
            number_match = re.search(r'(\d+)', file_name)
            figure_number = number_match.group(1) if number_match else '1'
            
            # 生成caption（这里可以根据需要调整）
            if figure_type == 'image':
                caption = f"Figure {figure_number}"
            else:
                caption = f"Table {figure_number}"
            
            figures.append({
                'figure_id': file_name,
                'caption': caption,
                'type': figure_type,
                'page_idx': 0,  # 暂时设为0，后续可以根据需要调整
                'bbox': None,   # figure_dict中没有bbox信息
                'base64_data': base64_data
            })
        
        return figures
    
    def _extract_figures_from_merged_data(self, merged_data: List[Dict]) -> List[Dict]:
        """从合并数据中提取图表信息"""
        figures = []
        
        for item in merged_data:
            # 处理图片
            if item.get('type') == 'image' and item.get('image_caption'):
                caption = item['image_caption']
                if isinstance(caption, list):
                    caption = ' '.join(caption)
                
                # 从img_path提取figure_id (注意：字段名是img_path不是image_path)
                image_path = item.get('img_path', '')
                figure_id = self._extract_id_from_path(image_path)
                
                print(f"📷 提取图片 - 路径: {image_path}, ID: {figure_id}")
                
                figures.append({
                    'figure_id': figure_id,
                    'caption': caption,
                    'type': 'image',
                    'page_idx': item.get('page_idx', 0),
                    'bbox': item.get('bbox')
                })
            
            # 处理表格
            elif item.get('type') == 'table' and item.get('table_caption'):
                caption = item['table_caption']
                if isinstance(caption, list):
                    caption = ' '.join(caption)
                
                # 从img_path提取table_id (表格也用img_path存储)
                table_path = item.get('img_path', '')
                table_id = self._extract_id_from_path(table_path)
                
                print(f"📋 提取表格 - 路径: {table_path}, ID: {table_id}")
                
                figures.append({
                    'figure_id': table_id,
                    'caption': caption,
                    'type': 'table',
                    'page_idx': item.get('page_idx', 0),
                    'bbox': item.get('bbox')
                })
        
        return figures
    
    def _extract_references_from_merged_data(self, merged_data: List[Dict]) -> List[Dict]:
        """从merged_data中提取引用，保留位置信息"""
        references = []
        
        for item in merged_data:
            # 只处理文本类型的数据
            if item.get('type') == 'text' and item.get('text'):
                text = item['text']
                page_idx = item.get('page_idx', 0)
                bbox = item.get('bbox')
            else:
                continue
            
            # 使用引用提取器找到引用
            text_references = self.extractor.extract_references(text)
            
            # 为每个引用添加位置信息
            for ref in text_references:
                ref['page_idx'] = page_idx
                ref['bbox'] = bbox
                references.append(ref)
        
        text_blocks = [item for item in merged_data if isinstance(item, str) or (isinstance(item, dict) and item.get('type') == 'text')]
        print(f"🔍 从 {len(text_blocks)} 个文本块中提取引用")
        
        # 去重：移除重复的引用
        unique_references = []
        seen_refs = set()
        
        for ref in references:
            # 使用句子+编号+类型作为唯一键
            ref_key = (ref['sentence'].strip(), ref['number'], ref['ref_type'])
            if ref_key not in seen_refs:
                seen_refs.add(ref_key)
                unique_references.append(ref)
        
        print(f"📝 去重后剩余 {len(unique_references)} 个唯一引用")
        return unique_references
    
    def _extract_id_from_path(self, path: str) -> str:
        """从路径中提取ID"""
        if not path:
            return "unknown"
        
        # 提取文件名 (去掉路径和扩展名)
        import os
        filename = os.path.splitext(os.path.basename(path))[0]
        return filename
    
    def _match_figure_with_references(self, figure: Dict, references: List[Dict]) -> List[Dict]:
        """为单个图表匹配相关引用 - 基于编号匹配"""
        print(f"调试: figure类型: {type(figure)}, 内容: {figure}")
        # 从标题中提取编号
        figure_number = EnhancementModules.extract_figure_number_from_caption(figure['caption'])
        figure_type = EnhancementModules.extract_figure_type_from_caption(figure['caption'])
        
        if not figure_number:
            print(f"⚠️  无法从标题中提取编号: {figure['caption'][:50]}...")
            return []
        
        print(f"🔍 匹配 {figure_type} {figure_number}: {figure['caption'][:50]}...")
        
        matches = []
        seen_sentences = set()  # 用于去重
        
        for ref in references:
            # 严格的编号和类型匹配
            if (ref['number'] == figure_number and 
                ref['ref_type'] == figure_type):
                
                # 去重：避免同一个句子被多次匹配
                sentence_key = ref['sentence'].strip()
                if sentence_key in seen_sentences:
                    continue
                seen_sentences.add(sentence_key)
                
                # 计算位置权重（支持bbox上下方向判断）
                position_weight = self._calculate_position_weight(figure, ref)
                
                matches.append({
                    'reference_text': ref['sentence'],
                    'match_text': ref['match_text'],
                    'page_distance': abs(figure['page_idx'] - ref.get('page_idx', 0)),
                    'position_weight': position_weight,
                    'confidence_score': position_weight  # 简化的置信度分数
                })
        
        # 按位置权重排序
        matches.sort(key=lambda x: x['position_weight'], reverse=True)
        
        print(f"   找到 {len(matches)} 个匹配")
        return matches
    
    def _calculate_position_weight(self, figure: Dict, reference: Dict) -> float:
        """计算位置权重 - 支持同页面内的上下方向和跨页面距离"""
        fig_page = figure.get('page_idx', 0)
        ref_page = reference.get('page_idx', 0)
        
        # 跨页面的情况：使用页面距离权重
        if fig_page != ref_page:
            page_distance = abs(fig_page - ref_page)
            if page_distance == 1:
                return 0.8  # 相邻页高权重
            elif page_distance <= 3:
                return 0.6  # 近距离页面中等权重
            else:
                return 0.3  # 远距离页面低权重
        
        # 同页面的情况：使用bbox位置判断上下关系
        fig_bbox = figure.get('bbox')
        ref_bbox = reference.get('bbox')
        
        if fig_bbox and ref_bbox and len(fig_bbox) >= 4 and len(ref_bbox) >= 4:
            # bbox格式: [x1, y1, x2, y2]
            fig_y = fig_bbox[1]  # 图片的顶部y坐标
            ref_y = ref_bbox[1]  # 引用文本的顶部y坐标
            
            # PDF坐标系：y坐标越小越靠上
            if ref_y < fig_y:
                print(f"   📍 引用在图片上方 (ref_y: {ref_y} < fig_y: {fig_y})")
                return 1.0  # 图片上方的引用（预先引用）
            else:
                print(f"   📍 引用在图片下方 (ref_y: {ref_y} > fig_y: {fig_y})")
                return 1.0  # 图片下方的引用（后续说明）
        else:
            print(f"   ⚠️ 缺少bbox信息，使用默认同页权重")
            return 1.0  # 同页面但无法确定上下关系，给予最高权重
    
    def _format_output(self, results: List[Dict], document_id: str = None) -> Dict:
        """格式化输出结果"""
        total_matches = sum(len(r['matches']) for r in results)
        
        output = {
            'document_id': document_id or 'unknown',
            'total_figures': len(results),
            'total_matches': total_matches,
            'results': results,
            'statistics': {
                'figures_with_matches': len([r for r in results if r['matches']]),
                'figures_without_matches': len([r for r in results if not r['matches']]),
                'average_matches_per_figure': total_matches / len(results) if results else 0
            }
        }
        
        return output