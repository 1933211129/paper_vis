"""
标题映射LLM模块
利用LLM对论文章节标题进行分类映射到四个标准泳道
"""

import json
import requests
import logging
from typing import List, Dict, Optional, Any
import time
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL

class TitleMappingLLM:
    """标题映射LLM处理器"""
    
    def __init__(self, api_url: str = None, api_key: str = None, model: str = None):
        """
        初始化LLM处理器
        
        Args:
            api_url: LLM API地址
            api_key: API密钥
            model: 使用的模型名称
        """
        # 写死的LLM配置
        self.api_url = api_url or DEEPSEEK_API_URL
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.model = model or DEEPSEEK_MODEL
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 系统提示词
        self.system_prompt = """You are a top-tier **Academic Paper Structure Analyst** specializing in **cross-disciplinary semantic filtering and classification**. Your task is to accurately map chapter titles, which represent the **core research logic flow**, from a provided list of titles into four standard swimlanes.

**[Core Filtering and Mapping Rules]**
1.  **Filtering (Noise Reduction):** You must **ignore and discard** the following types of titles:
    * **Non-chapter content:** Paper main titles, author lists, publication metadata (e.g., "Article", "Online content", "Check for updates", "Reporting summary", "Data availability", "Author contributions", "Competing interests", etc.).
    * **Boundary anchors:** "Abstract" (or its variants), "References", "Acknowledgements", "Appendix".
2.  **Lane Assignment (Classification):** Only assign the filtered **valid core chapters** to the following **Four Standard Swimlanes**.
3.  **Quota Constraint (Max: 2):** The number of titles assigned to each standard swimlane **must not exceed two (Max: 2)**. If multiple titles belong to the same swimlane, you must select the core titles that best represent the function of that swimlane.

**[Four Standard Swimlanes]**
1.  Context & Related Work
2.  Methodology & Setup
3.  Results & Analysis
4.  Conclusion

**[CRITICAL FORMATTING REQUIREMENTS]**
1.  **Strictly and uniquely** output a JSON object conforming to the JSON structure.
2.  The Key must be the **Standard Swimlane Name**, and the Value must be an **array** containing the **EXACT original title strings**.
3.  **PRESERVE EXACT FORMAT:** You MUST preserve the exact original format of titles including ALL symbols, numbers, punctuation, capitalization, and spacing (e.g., "# 1. Introduction", "# 2. Related Work", etc.).
4.  **Absolutely forbid** outputting any explanations, preambles, summaries, or extra text."""

        # 用户提示词模板
        self.user_prompt_template = """Please analyze the **raw title list** provided below, which originates from a paper parser. Strictly adhere to the **filtering and quota constraints** rules specified in the system instructions to classify and map the core chapter titles into the four standard swimlanes.

**[Title List to be Processed]**
{title_list}

**[Example of Desired JSON Structure]**
Please strictly output your results according to the following concise structure, where the **Key is the Swimlane Name and the Value is an array of EXACT original title strings** (preserving all formatting including "#", numbers, punctuation):

{{
  "Context & Related Work": ["# 1. Introduction", "# 2. Related Work"],
  "Methodology & Setup": ["# 3. Methodology"],
  "Results & Analysis": ["# 4. Results", "# 5. Discussion"],
  "Conclusion": ["# 6. Conclusion"]
}}"""

    def _call_llm_api(self, messages: List[Dict[str, str]], max_retries: int = 3) -> Optional[str]:
        """
        调用LLM API
        
        Args:
            messages: 消息列表
            max_retries: 最大重试次数
            
        Returns:
            LLM响应内容
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,  # 低温度确保一致性
            "max_tokens": 1000
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    self.logger.warning(f"API调用失败，状态码: {response.status_code}, 响应: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"API调用异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
                
        self.logger.error("LLM API调用失败，已达到最大重试次数")
        return None

    def _parse_json_response(self, response: str) -> Optional[Dict[str, List[str]]]:
        """
        解析LLM返回的JSON响应
        
        Args:
            response: LLM响应字符串
            
        Returns:
            解析后的字典，如果解析失败返回None
        """
        try:
            # 尝试直接解析
            result = json.loads(response)
            
            # 验证结构
            expected_keys = {
                "Context & Related Work",
                "Methodology & Setup", 
                "Results & Analysis",
                "Conclusion"
            }
            
            if not all(key in result for key in expected_keys):
                self.logger.warning("JSON结构不完整，缺少必要的键")
                return None
                
            # 验证值类型
            for key, value in result.items():
                if not isinstance(value, list):
                    self.logger.warning(f"键 '{key}' 的值不是列表类型")
                    return None
                    
            return result
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON解析失败: {e}")
            
            # 尝试提取JSON部分
            try:
                # 查找JSON开始和结束位置
                start_idx = response.find('{')
                end_idx = response.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx + 1]
                    result = json.loads(json_str)
                    return result
                    
            except json.JSONDecodeError:
                pass
                
            return None

    def map_titles(self, title_list: List[str]) -> Dict[str, List[str]]:
        """
        将标题列表映射到四个标准泳道
        
        Args:
            title_list: 原始标题列表
            
        Returns:
            干净的映射结果字典
        """
        if not title_list:
            self.logger.error("标题列表为空")
            return {}
            
        if not self.api_key:
            self.logger.error("API密钥未设置")
            return {}
        
        try:
            # 构建用户提示词
            title_list_str = "\n".join([f"'{title}'" for title in title_list])
            user_prompt = self.user_prompt_template.format(title_list=title_list_str)
            
            # 构建消息
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            self.logger.info(f"开始处理 {len(title_list)} 个标题")
            
            # 调用LLM API
            response = self._call_llm_api(messages)
            
            if response is None:
                self.logger.error("LLM API调用失败")
                return {}
            
            # 解析响应
            result = self._parse_json_response(response)
            
            if result is None:
                self.logger.error(f"LLM响应解析失败，原始响应: {response}")
                return {}
            
            # 验证结果
            total_mapped = sum(len(titles) for titles in result.values())
            self.logger.info(f"成功映射 {total_mapped} 个标题到四个泳道")
            
            return result
            
        except Exception as e:
            self.logger.error(f"标题映射过程中发生异常: {e}")
            return {}

    def map_titles_with_debug(self, title_list: List[str]) -> Dict[str, List[str]]:
        """
        标题映射（保持向后兼容）
        
        Args:
            title_list: 原始标题列表
            
        Returns:
            干净的映射结果字典
        """
        return self.map_titles(title_list)


def main():
    """测试函数"""
    # 示例使用
    title_list = [
        "# A Q-learning approach to the continuous control problem of robot inverted pendulum balancing",
        "# Corresponding Author:",
        "# Abstract",
        "# 1. Introduction",
        "# 2. Proposed approach and background", 
        "# 3. Methodologies",
        "# 4. Results and discussion",
        "# 5. Conclusion",
        "# Acknowledgements",
        "# References"
    ]
    
    # 初始化处理器（需要设置API密钥）
    mapper = TitleMappingLLM()
    
    # 执行映射
    result = mapper.map_titles_with_debug(title_list)
    print(result)


if __name__ == "__main__":
    main()
