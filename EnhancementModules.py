from typing import List, Dict, Optional

class EnhancementModules:
    @staticmethod
    def calculate_position_distance(figure_page: int, reference_page: int) -> float:
        """计算位置距离权重 - 页面距离越近权重越高"""
        page_distance = abs(figure_page - reference_page)
        
        if page_distance == 0:
            return 1.0  # 同一页最高权重
        elif page_distance == 1:
            return 0.8  # 相邻页高权重
        elif page_distance <= 3:
            return 0.6  # 近距离页面中等权重
        else:
            return 0.3  # 远距离页面低权重
    
    @staticmethod
    def extract_figure_number_from_caption(caption: str) -> Optional[str]:
        """从图表标题中提取编号"""
        import re
        
        # 提取图片编号
        fig_match = re.search(r'(?:Fig\.|Figure|FIG\.?)\s*(\d+)', caption, re.IGNORECASE)
        if fig_match:
            return fig_match.group(1)
        
        # 提取表格编号  
        table_match = re.search(r'(?:Table|Tab\.|TABLE\.?)\s*(\d+)', caption, re.IGNORECASE)
        if table_match:
            return table_match.group(1)
        
        return None
    
    @staticmethod
    def extract_figure_type_from_caption(caption: str) -> str:
        """从标题中判断是图片还是表格"""
        import re
        
        if re.search(r'\b(?:Table|Tab\.|TABLE\.?)', caption, re.IGNORECASE):
            return 'table'
        elif re.search(r'\b(?:Fig\.|Figure|FIG\.?)', caption, re.IGNORECASE):
            return 'figure'
        else:
            return 'unknown'