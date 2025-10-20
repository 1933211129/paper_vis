import re
from typing import List, Dict

class FigureReferenceExtractor:
    def __init__(self):
        # 全面的图片引用模式 - 覆盖所有可能的变体
        self.figure_patterns = [
            # 基础英文模式
            r'\b(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)',
            r'\((?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)\)',
            r'\[(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)\]',
            
            # 带修饰词的模式
            r'\b(?:see|See|refer to|Refer to|shown in|Shown in|as in|As in)\s+(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)',
            r'\b(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)\s*(?:shows|depicts|illustrates|presents|displays)',
            r'\b(?:The|the)\s+(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)',
            
            # 上下文引用
            r'\b(?:above|below|following|previous|next|aforementioned|aforesaid)\s+(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)',
            r'\b(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)\s*(?:above|below|shown|presented)',
            
            # 中英混合模式
            r'如\s*(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)\s*所示',
            r'见\s*(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)',
            r'参见\s*(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)',
            r'\(见\s*(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)\)',
            r'\(参见\s*(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)\)',
            
            # 纯中文模式
            r'图\s*(\d+)',
            r'第\s*(\d+)\s*图',
            r'见图\s*(\d+)',
            r'如图\s*(\d+)\s*所示',
            r'参见图\s*(\d+)',
            r'\(图\s*(\d+)\)',
            r'\(见图\s*(\d+)\)',
            
            # 变体和缩写
            r'\bfig\s*(\d+)',
            r'\bFig\s*(\d+)',
            r'\bFigure\s*(\d+)',
            r'figure\s*(\d+)',
            
            # 带标点的模式
            r'(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)[,，.]',
            r'(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)[：:]',
            
            # 连接词模式
            r'\b(?:in|In)\s+(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)',
            r'\b(?:from|From)\s+(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)',
            r'\b(?:of|Of)\s+(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)',
            
            # 描述性引用
            r'\b(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)\s*(?:demonstrates|reveals|indicates|suggests)',
            r'\b(?:According to|according to)\s+(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)',
            r'\b(?:Based on|based on)\s+(?:Fig\.|Figure|FIG\.?|fig\.?)\s*(\d+)',
        ]
        
        # 全面的表格引用模式 - 覆盖所有可能的变体
        self.table_patterns = [
            # 基础英文模式
            r'\b(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            r'\((?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)\)',
            r'\[(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)\]',
            
            # 带修饰词的模式
            r'\b(?:see|See|refer to|Refer to|shown in|Shown in|as in|As in)\s+(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            r'\b(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)\s*(?:shows|lists|presents|summarizes|contains)',
            r'\b(?:The|the)\s+(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            
            # 上下文引用
            r'\b(?:above|below|following|previous|next|aforementioned|aforesaid)\s+(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            r'\b(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)\s*(?:above|below|shown|presented)',
            
            # 数据相关引用
            r'\b(?:data|Data|results|Results|statistics|Statistics)\s+(?:in|from|of)\s+(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            r'\b(?:summarized|presented|listed|shown|reported)\s+in\s+(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            
            # 中英混合模式
            r'如\s*(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)\s*所示',
            r'见\s*(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            r'参见\s*(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            r'\(见\s*(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)\)',
            r'\(参见\s*(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)\)',
            
            # 纯中文模式
            r'表\s*(\d+)',
            r'第\s*(\d+)\s*表',
            r'见表\s*(\d+)',
            r'如表\s*(\d+)\s*所示',
            r'参见表\s*(\d+)',
            r'\(表\s*(\d+)\)',
            r'\(见表\s*(\d+)\)',
            
            # 变体和缩写
            r'\btab\s*(\d+)',
            r'\bTab\s*(\d+)',
            r'\bTable\s*(\d+)',
            r'table\s*(\d+)',
            
            # 带标点的模式
            r'(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)[,，.]',
            r'(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)[：:]',
            
            # 连接词模式
            r'\b(?:in|In)\s+(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            r'\b(?:from|From)\s+(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            r'\b(?:of|Of)\s+(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            
            # 描述性引用
            r'\b(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)\s*(?:demonstrates|reveals|indicates|suggests|provides)',
            r'\b(?:According to|according to)\s+(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
            r'\b(?:Based on|based on)\s+(?:Table|Tab\.|TABLE\.?|table|tab\.?)\s*(\d+)',
        ]
    
    def extract_references(self, text: str) -> List[Dict]:
        """提取文本中的图表引用 - 简化版本，只匹配明确编号"""
        sentences = self._split_sentences(text)
        references = []
        
        for sent_idx, sentence in enumerate(sentences):
            # 跳过太短的句子
            if len(sentence.strip()) < 10:
                continue
                
            # 检查图片引用
            for pattern in self.figure_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    number = match.group(1)
                    references.append({
                        'sentence': sentence.strip(),
                        'sentence_idx': sent_idx,
                        'ref_type': 'figure',
                        'number': number,
                        'match_text': match.group()
                    })
            
            # 检查表格引用
            for pattern in self.table_patterns:
                matches = re.finditer(pattern, sentence, re.IGNORECASE)
                for match in matches:
                    number = match.group(1)
                    references.append({
                        'sentence': sentence.strip(),
                        'sentence_idx': sent_idx,
                        'ref_type': 'table',
                        'number': number,
                        'match_text': match.group()
                    })
        
        return references
    
    def _split_sentences(self, text: str) -> List[str]:
        """智能句子分割 - 避免在图表引用处错误分割"""
        # 先保护图表引用，避免在Fig. Table.等处分割
        protected_text = text
        
        # 保护常见的图表引用模式 - 替换句号避免分割
        protection_patterns = [
            (r'\b(Fig\.)\s*(\d+)', r'\1___SPACE___\2'),
            (r'\b(Table\.)\s*(\d+)', r'\1___SPACE___\2'),
            (r'\b(Tab\.)\s*(\d+)', r'\1___SPACE___\2'),
        ]
        
        for pattern, replacement in protection_patterns:
            protected_text = re.sub(pattern, replacement, protected_text, flags=re.IGNORECASE)
        
        # 现在进行句子分割
        sentences = re.split(r'[.!?]\s+', protected_text)
        
        # 恢复保护的图表引用
        restored_sentences = []
        for sentence in sentences:
            sentence = sentence.replace('___SPACE___', ' ')
            if sentence.strip():
                restored_sentences.append(sentence.strip())
        
        return restored_sentences