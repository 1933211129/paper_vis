import json
import os
from typing import Dict, List, Optional
from difflib import SequenceMatcher

class DataMerger:
    def __init__(self):
        self.similarity_threshold = 0.6  # 文本相似度阈值
        
    def merge_data(self, content_list: List[Dict], middle_data: Dict) -> List[Dict]:
        """
        合并content_list和middle数据（内存处理）
        
        Args:
            content_list: content_list数据列表
            middle_data: middle数据字典
        
        Returns:
            List[Dict]: 合并后的数据列表
        """
        print("正在处理数据...")
        
        print(f"content_list: {len(content_list)} 条记录")
        print(f"middle_data: {len(middle_data['pdf_info'])} 页数据")
        
        # 构建middle数据索引
        middle_index = self._build_middle_index(middle_data)
        
        # 合并数据
        merged_data = []
        matched_count = 0
        
        for item in content_list:
            # 处理字符串格式的content_list
            if isinstance(item, str):
                # 将字符串转换为字典格式
                merged_item = {
                    'type': 'text',
                    'text': item,
                    'page_idx': 0  # 默认页面
                }
            else:
                merged_item = item.copy()  # 保留原有字段
            
            # 查找匹配的middle数据
            bbox_info = self._find_matching_bbox(item, middle_index)
            
            if bbox_info:
                merged_item.update(bbox_info)
                matched_count += 1
                print(f"✅ 匹配成功: {item.get('type')} - {bbox_info.get('match_method')} - 置信度: {bbox_info.get('match_confidence', 0):.3f}")
            else:
                # 未匹配到bbox信息，添加空的位置信息
                merged_item.update({
                    'bbox': None,
                    'middle_type': None,
                    'match_confidence': 0.0,
                    'match_method': 'no_match'
                })
                print(f"❌ 未匹配: {item.get('type')} - 页面: {item.get('page_idx')} - 内容: {str(item.get('img_caption', item.get('text', '')))[:50]}...")
            
            merged_data.append(merged_item)
        
        print(f"✅ 数据合并完成!")
        print(f"   - 总记录数: {len(merged_data)}")
        print(f"   - 成功匹配: {matched_count}")
        print(f"   - 匹配率: {matched_count/len(merged_data)*100:.1f}%")
        print(f"调试: merged_data前3项类型: {[type(item) for item in merged_data[:3]]}")
        
        return merged_data
    
    def _build_middle_index(self, middle_data: Dict) -> Dict:
        """构建middle数据的索引结构"""
        index = {}
        
        print(f"构建索引: 共 {len(middle_data['pdf_info'])} 页数据")
        
        for array_idx, page_info in enumerate(middle_data['pdf_info']):
            print(f"调试: page_info类型: {type(page_info)}")
            if isinstance(page_info, str):
                print(f"警告: page_info是字符串，跳过处理")
                continue
            # 获取实际页面号，优先使用page_idx字段，否则用数组索引
            actual_page_idx = page_info.get('page_idx', array_idx)
            print(f"  处理页面: 数组索引={array_idx}, 实际页面={actual_page_idx}")
            
            index[actual_page_idx] = {
                'preproc_blocks': [],
                'para_blocks': []
            }
            
            # 统计image_caption和table_caption数量 - 修复：在blocks层级查找
            preproc_captions = 0
            para_captions = 0
            preproc_table_captions = 0
            para_table_captions = 0
            
            # 在preproc_blocks的blocks子数组中查找
            for block in page_info.get('preproc_blocks', []):
                for sub_block in block.get('blocks', []):
                    if sub_block.get('type') == 'image_caption':
                        preproc_captions += 1
                    elif sub_block.get('type') == 'table_caption':
                        preproc_table_captions += 1
            
            # 在para_blocks的blocks子数组中查找
            for block in page_info.get('para_blocks', []):
                for sub_block in block.get('blocks', []):
                    if sub_block.get('type') == 'image_caption':
                        para_captions += 1
                    elif sub_block.get('type') == 'table_caption':
                        para_table_captions += 1
            
            print(f"    - preproc_blocks中的image_caption: {preproc_captions}个")
            print(f"    - para_blocks中的image_caption: {para_captions}个")
            print(f"    - preproc_blocks中的table_caption: {preproc_table_captions}个")
            print(f"    - para_blocks中的table_caption: {para_table_captions}个")
            
            # 索引preproc_blocks - 修复：查找blocks内的image_caption
            for block in page_info.get('preproc_blocks', []):
                # 处理顶层block
                block_info = {
                    'type': block.get('type'),
                    'bbox': block.get('bbox'),
                    'content': self._extract_content_from_block(block),
                    'first_span_bbox': self._get_first_span_bbox(block)
                }
                index[actual_page_idx]['preproc_blocks'].append(block_info)
                
                # 处理blocks数组内的image_caption和table_caption
                for sub_block in block.get('blocks', []):
                    if sub_block.get('type') in ['image_caption', 'table_caption']:
                        sub_block_info = {
                            'type': sub_block.get('type'),
                            'bbox': sub_block.get('bbox'),
                            'content': self._extract_content_from_block(sub_block),
                            'first_span_bbox': self._get_first_span_bbox(sub_block)
                        }
                        index[actual_page_idx]['preproc_blocks'].append(sub_block_info)
            
            # 索引para_blocks - 修复：查找blocks内的image_caption
            for block in page_info.get('para_blocks', []):
                # 处理顶层block
                block_info = {
                    'type': block.get('type'),
                    'bbox': block.get('bbox'),
                    'content': self._extract_content_from_block(block),
                    'first_span_bbox': self._get_first_span_bbox(block)
                }
                index[actual_page_idx]['para_blocks'].append(block_info)
                
                # 处理blocks数组内的image_caption和table_caption
                for sub_block in block.get('blocks', []):
                    if sub_block.get('type') in ['image_caption', 'table_caption']:
                        sub_block_info = {
                            'type': sub_block.get('type'),
                            'bbox': sub_block.get('bbox'),
                            'content': self._extract_content_from_block(sub_block),
                            'first_span_bbox': self._get_first_span_bbox(sub_block)
                        }
                        index[actual_page_idx]['para_blocks'].append(sub_block_info)
        
        return index
    
    def _extract_content_from_block(self, block: Dict) -> str:
        """从block中提取完整文本内容 - 更智能的拼接"""
        contents = []
        
        for line in block.get('lines', []):
            line_content = []
            for span in line.get('spans', []):
                content = span.get('content', '').strip()
                if content:
                    line_content.append(content)
            
            if line_content:
                # 如果行末没有句号等结束符，可能需要与下一行连接
                line_text = ' '.join(line_content)
                if line_text.endswith(('-', '—', '–')):
                    # 连字符结尾，去掉连字符直接连接
                    line_text = line_text[:-1]
                contents.append(line_text)
        
        # 智能连接：如果不是以句号结尾，直接连接；否则用空格连接
        result = ''
        for i, content in enumerate(contents):
            if i == 0:
                result = content
            else:
                # 如果前一个内容以连字符或不完整结尾，直接连接
                if (result.endswith(('-', '—', '–')) or 
                    not result.endswith(('.', '!', '?', ':'))):
                    result += content
                else:
                    result += ' ' + content
        
        return result
    
    def _get_first_span_bbox(self, block: Dict) -> Optional[List[int]]:
        """获取block中第一个span的bbox"""
        lines = block.get('lines', [])
        if not lines:
            return None
            
        spans = lines[0].get('spans', [])
        if not spans:
            return None
            
        return spans[0].get('bbox')
    
    def _find_matching_bbox(self, content_item, middle_index: Dict) -> Optional[Dict]:
        """为content_list中的item查找匹配的bbox信息"""
        # 处理字符串格式的content_item
        if isinstance(content_item, str):
            return None  # 字符串格式无法匹配bbox信息
        
        page_idx = content_item.get('page_idx')
        content_text = content_item.get('text', '').strip()
        content_type = content_item.get('type')
        
        if page_idx not in middle_index:
            return None
        
        # 特殊处理图片类型 - 使用img_caption匹配
        if content_type == 'image':
            print(f"\n🖼️ 处理图片: 页面 {page_idx}")
            if page_idx in middle_index:
                return self._find_image_caption_bbox(content_item, middle_index[page_idx])
            else:
                print(f"  ❌ 页面 {page_idx} 在middle_index中不存在")
                return None
        
        # 特殊处理表格类型 - 使用table_caption匹配
        if content_type == 'table':
            print(f"\n📊 处理表格: 页面 {page_idx}")
            if page_idx in middle_index:
                return self._find_table_caption_bbox(content_item, middle_index[page_idx])
            else:
                print(f"  ❌ 页面 {page_idx} 在middle_index中不存在")
                return None
        
        page_data = middle_index[page_idx]
        best_match = None
        best_score = 0
        
        # 在preproc_blocks和para_blocks中搜索
        for block_source in ['preproc_blocks', 'para_blocks']:
            for block in page_data[block_source]:
                # 计算文本相似度
                similarity = self._calculate_similarity(content_text, block['content'])
                
                # 类型匹配加分
                type_bonus = 0
                if self._type_match(content_type, block['type']):
                    type_bonus = 0.2
                
                total_score = similarity + type_bonus
                
                if total_score > best_score and similarity > self.similarity_threshold:
                    best_score = total_score
                    best_match = {
                        'bbox': block['bbox'],  # 使用block级bbox
                        'first_span_bbox': block['first_span_bbox'],  # 第一个span的bbox
                        'middle_type': block['type'],
                        'middle_content': block['content'],
                        'match_confidence': similarity,
                        'match_method': f'{block_source}_similarity',
                        'type_matched': bool(type_bonus > 0)
                    }
        
        return best_match
    
    def _find_image_caption_bbox(self, image_item: Dict, page_data: Dict) -> Optional[Dict]:
        """为图片查找对应的caption bbox"""
        img_caption = image_item.get('img_caption', [])
        if isinstance(img_caption, list):
            caption_text = ' '.join(img_caption)
        else:
            caption_text = str(img_caption)
        
        if not caption_text.strip():
            print(f"  - 图片caption为空，跳过")
            return None
        
        print(f"  - 查找图片caption: {caption_text[:100]}...")
        
        best_match = None
        best_score = 0
        candidates = []
        
        # 在image_caption类型的block中查找，优先搜索preproc_blocks
        search_order = ['preproc_blocks', 'para_blocks']
        for block_source in search_order:
            for block in page_data[block_source]:
                if block['type'] == 'image_caption':
                    # 计算caption文本相似度
                    similarity = self._calculate_similarity(caption_text, block['content'])
                    candidates.append((block, similarity, block_source))
                    
                    print(f"    - 候选: {block['content'][:80]}... 相似度: {similarity:.3f}")
                    
                    if similarity > best_score and similarity > 0.2:  # 降低到0.2，开头匹配策略下更宽松
                        best_score = similarity
                        best_match = {
                            'bbox': block['bbox'],  # 使用caption的bbox作为图片位置
                            'first_span_bbox': block['first_span_bbox'],
                            'middle_type': 'image_caption',
                            'middle_content': block['content'],
                            'match_confidence': similarity,
                            'match_method': f'image_caption_{block_source}',
                            'type_matched': True
                        }
        
        if best_match:
            print(f"  ✅ 找到最佳匹配: {best_score:.3f}")
        else:
            print(f"  ❌ 未找到匹配 (共检查了 {len(candidates)} 个候选)")
            # 如果没有找到，尝试更宽松的匹配：只要包含Figure关键字
            print(f"  🔄 尝试宽松匹配...")
            for block_source in search_order:
                for block in page_data[block_source]:
                    if (block['type'] == 'image_caption' and 
                        'figure' in block['content'].lower() and
                        'figure' in caption_text.lower()):
                        
                        # 提取图号进行匹配
                        import re
                        fig_num_pattern = r'figure\s*(\d+)'
                        caption_nums = re.findall(fig_num_pattern, caption_text.lower())
                        block_nums = re.findall(fig_num_pattern, block['content'].lower())
                        
                        if caption_nums and block_nums and caption_nums[0] == block_nums[0]:
                            print(f"    💡 图号匹配: Figure {caption_nums[0]}")
                            best_match = {
                                'bbox': block['bbox'],
                                'first_span_bbox': block['first_span_bbox'],
                                'middle_type': 'image_caption',
                                'middle_content': block['content'],
                                'match_confidence': 0.8,  # 图号匹配给高置信度
                                'match_method': f'figure_number_{block_source}',
                                'type_matched': True
                            }
                            print(f"  ✅ 图号匹配成功: {caption_nums[0]}")
                            break
                if best_match:
                    break
            
        return best_match
    
    def _find_table_caption_bbox(self, table_item: Dict, page_data: Dict) -> Optional[Dict]:
        """为表格查找对应的caption bbox"""
        table_caption = table_item.get('table_caption', [])
        if isinstance(table_caption, list):
            caption_text = ' '.join(table_caption)
        else:
            caption_text = str(table_caption)
        
        if not caption_text.strip():
            print(f"  - 表格caption为空，跳过")
            return None
        
        print(f"  - 查找表格caption: {caption_text[:100]}...")
        
        best_match = None
        best_score = 0
        candidates = []
        
        # 在table_caption类型的block中查找，优先搜索preproc_blocks
        search_order = ['preproc_blocks', 'para_blocks']
        for block_source in search_order:
            for block in page_data[block_source]:
                if block['type'] == 'table_caption':
                    # 计算caption文本相似度
                    similarity = self._calculate_similarity(caption_text, block['content'])
                    candidates.append((block, similarity, block_source))
                    
                    print(f"    - 候选: {block['content'][:80]}... 相似度: {similarity:.3f}")
                    
                    if similarity > best_score and similarity > 0.2:  # 降低到0.2，开头匹配策略下更宽松
                        best_score = similarity
                        best_match = {
                            'bbox': block['bbox'],  # 使用caption的bbox作为表格位置
                            'first_span_bbox': block['first_span_bbox'],
                            'middle_type': 'table_caption',
                            'middle_content': block['content'],
                            'match_confidence': similarity,
                            'match_method': f'table_caption_{block_source}',
                            'type_matched': True
                        }
        
        if best_match:
            print(f"  ✅ 找到最佳匹配: {best_score:.3f}")
        else:
            print(f"  ❌ 未找到匹配 (共检查了 {len(candidates)} 个候选)")
            # 如果没有找到，尝试更宽松的匹配：只要包含Table关键字
            print(f"  🔄 尝试宽松匹配...")
            for block_source in search_order:
                for block in page_data[block_source]:
                    if (block['type'] == 'table_caption' and 
                        'table' in block['content'].lower() and
                        'table' in caption_text.lower()):
                        
                        # 提取表号进行匹配
                        import re
                        table_num_pattern = r'table\s*(\d+)'
                        caption_nums = re.findall(table_num_pattern, caption_text.lower())
                        block_nums = re.findall(table_num_pattern, block['content'].lower())
                        
                        if caption_nums and block_nums and caption_nums[0] == block_nums[0]:
                            print(f"    💡 表号匹配: Table {caption_nums[0]}")
                            best_match = {
                                'bbox': block['bbox'],
                                'first_span_bbox': block['first_span_bbox'],
                                'middle_type': 'table_caption',
                                'middle_content': block['content'],
                                'match_confidence': 0.8,  # 表号匹配给高置信度
                                'match_method': f'table_number_{block_source}',
                                'type_matched': True
                            }
                            print(f"  ✅ 表号匹配成功: {caption_nums[0]}")
                            break
                if best_match:
                    break
            
        return best_match
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度 - 开头匹配优先策略"""
        if not text1 or not text2:
            return 0.0
        
        # 清理文本：移除多余空格、标点，统一大小写
        text1_clean = self._clean_text_for_comparison(text1)
        text2_clean = self._clean_text_for_comparison(text2)
        
        # 1. 开头匹配检查 (关键策略!)
        # 取较短文本的80%长度作为开头匹配
        min_len = min(len(text1_clean), len(text2_clean))
        prefix_len = max(10, int(min_len * 0.8))
        
        text1_prefix = text1_clean[:prefix_len]
        text2_prefix = text2_clean[:prefix_len]
        
        prefix_ratio = SequenceMatcher(None, text1_prefix, text2_prefix).ratio()
        
        # 2. 如果开头匹配度很高，直接给高分
        if prefix_ratio >= 0.8:
            return min(0.9 + prefix_ratio * 0.1, 1.0)
        
        # 3. 序列相似度
        seq_ratio = SequenceMatcher(None, text1_clean, text2_clean).ratio()
        
        # 4. 包含关系检查
        if text1_clean in text2_clean or text2_clean in text1_clean:
            contain_bonus = 0.3
        else:
            contain_bonus = 0
        
        # 5. 关键词匹配度
        words1 = set(text1_clean.split())
        words2 = set(text2_clean.split())
        if words1 and words2:
            word_overlap = len(words1 & words2) / len(words1 | words2)
        else:
            word_overlap = 0
        
        # 综合计算：优先考虑开头匹配
        final_score = prefix_ratio * 0.5 + seq_ratio * 0.3 + word_overlap * 0.2 + contain_bonus
        return min(final_score, 1.0)
    
    def _clean_text_for_comparison(self, text: str) -> str:
        """清理文本用于比较"""
        import re
        # 移除标点符号，保留字母数字和空格
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        # 移除多余空格
        text = ' '.join(text.split())
        return text
    
    def _type_match(self, content_type: str, middle_type: str) -> bool:
        """判断类型是否匹配"""
        type_mapping = {
            'text': ['text', 'paragraph', 'para'],
            'image': ['image', 'figure'],
            'title': ['title', 'heading'],
            'table': ['table']
        }
        
        if content_type in type_mapping:
            return middle_type in type_mapping[content_type]
        
        return content_type == middle_type

def main():
    """主函数示例"""
    merger = DataMerger()
    
    # 示例用法
    content_list_path = "../arxiv/1ee8ca1c-3478-4c4f-9b77-379ff4d58982/2dbbabd2678ba74fcd9b08aadae975ae_content_list.json"
    middle_path = "../arxiv/1ee8ca1c-3478-4c4f-9b77-379ff4d58982/2dbbabd2678ba74fcd9b08aadae975ae_middle.json"
    output_path = "merged_data.json"
    
    # 检查文件是否存在
    if not os.path.exists(content_list_path):
        print(f"错误: 找不到文件 {content_list_path}")
        return
        
    if not os.path.exists(middle_path):
        print(f"错误: 找不到文件 {middle_path}")
        return
    
    # 执行合并
    try:
        merged_data = merger.merge_data(content_list_path, middle_path, output_path)
    except Exception as e:
        print(f"❌ 合并过程中出错: {e}")

if __name__ == "__main__":
    main()
