#!/usr/bin/env python3
"""
学术创新机会发现功能类
基于PDF解析结果和泳道内容提取进行创新机会识别
"""

import json
import requests
import sys
import os
from typing import Dict, Any, Optional

# 添加functions目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'functions'))

from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL, MAX_RETRIES, MAX_TOKENS, TEMPERATURE

class InnovationDiscovery:
    """学术创新机会发现类"""
    
    def __init__(self):
        """初始化创新发现类"""
        self.api_key = DEEPSEEK_API_KEY
        self.api_url = DEEPSEEK_API_URL
        self.model = DEEPSEEK_MODEL
        self.max_retries = MAX_RETRIES
        self.max_tokens = MAX_TOKENS
        self.temperature = TEMPERATURE

    def _build_prompt_for_raw_texts(self, abstract_excerpt: str, conclusion_text: str) -> str:
        """构造面向两段原始文本的提示词（不依赖结构化输入）。"""
        return f"""You are an expert academic research analyst. Your sole function is to identify 5 high-potential academic innovation opportunities from TWO raw text sources of a scientific paper:

1) Paper content excerpt (first 5000 characters from the paper's markdown content):
---BEGIN_PAPER_EXCERPT---
{abstract_excerpt}
---END_PAPER_EXCERPT---

2) Conclusion section text (raw conclusion text from the paper):
---BEGIN_CONCLUSION_TEXT---
{conclusion_text}
---END_CONCLUSION_TEXT---

Strict constraints:
- Use ONLY the information from the two sources above. Do NOT hallucinate.
- Focus on explicit limitations, future work, and research gaps mentioned in the conclusion text.
- Cross-reference with the paper excerpt to validate and contextualize opportunities.
- Be precise and actionable. Avoid generic or banal suggestions.

Task:
- Produce EXACTLY 5 innovation opportunities as a SINGLE, VALID JSON OBJECT. No extra words or markdown fences.

Output JSON schema:
{{
  "Limitation Breakthrough": "Concise analysis addressing a stated limitation from the conclusion or paper content.",
  "Methodological Improvement": "A specific, technically plausible improvement or alternative to the core method.",
  "Application Expansion": "A novel task/domain/application where the method can transfer or adapt.",
  "[Dynamic Title 1]": "A unique, open-ended research insight inspired by the paper (provide a detailed description).",
  "[Dynamic Title 2]": "Another unique, open-ended research insight inspired by the paper (provide a detailed description)."
}}

IMPORTANT: For the last two fields, replace "[Dynamic Title 1]" and "[Dynamic Title 2]" with your own creative titles (maximum 5 words each). The titles should be the keys, and the descriptions should be the values.

Formatting rules:
- Output ONLY the raw JSON object. NO explanations. NO ```json fences. NO comments.
- Keep each value under 120 English words, be specific and actionable.
- Focus on opportunities that build upon or extend the paper's contributions.
"""


    def call_innovation_discovery_from_raw(self, abstract_excerpt: str, conclusion_text: str) -> Dict[str, Any]:
        """调用创新机会发现API（使用两段原始文本）。"""
        prompt = self._build_prompt_for_raw_texts(abstract_excerpt or "", conclusion_text or "")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()

                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                return json.loads(content)
            except requests.exceptions.RequestException as e:
                print(f"API请求失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise
            except json.JSONDecodeError as e:
                print(f"JSON解析失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                print(f"原始响应: {content}")
                if attempt == self.max_retries - 1:
                    raise
            except Exception as e:
                print(f"未知错误 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise


    def analyze_innovation_discovery_sync(self, input_bundle: str) -> Optional[Dict[str, Any]]:
        """
        同步分析入口：接收 LaneExtractor 传入的字符串（JSON），包含两段原始文本：
        - abstract_excerpt: 摘要前5000字符
        - conclusion_text: 结论原文
        返回：符合 schema 的 JSON 对象；失败返回 None。
        """
        try:
            data = json.loads(input_bundle) if input_bundle else {}
            abstract_excerpt = data.get('abstract_excerpt', '')
            conclusion_text = data.get('conclusion_text', '')
        except Exception as e:
            print(f"输入解析失败: {e}")
            abstract_excerpt, conclusion_text = "", ""

        try:
            result = self.call_innovation_discovery_from_raw(abstract_excerpt, conclusion_text)
            return result if isinstance(result, dict) and len(result.keys()) >= 5 else None
        except Exception as e:
            print(f"创新发现调用失败: {e}")
            return None
    
    def discover_innovation_opportunities(self, paper_excerpt: str, conclusion_text: str) -> Optional[Dict[str, Any]]:
        """
        基于论文内容摘要和结论文本发现创新机会
        
        Args:
            paper_excerpt: 论文内容前5000字符
            conclusion_text: 结论部分原文
            
        Returns:
            创新机会字典，包含5个创新机会，失败返回None
        """
        try:
            result = self.call_innovation_discovery_from_raw(paper_excerpt, conclusion_text)
            return result if isinstance(result, dict) and len(result.keys()) >= 5 else None
        except Exception as e:
            print(f"创新机会发现失败: {e}")
            return None


def analyze_innovation_discovery_sync(input_bundle: str) -> Optional[Dict[str, Any]]:
    """
    独立的同步分析函数，供LaneExtractor调用
    
    Args:
        input_bundle: JSON字符串，包含abstract_excerpt和conclusion_text
    
    Returns:
        创新机会字典，失败返回None
    """
    try:
        discovery = InnovationDiscovery()
        return discovery.analyze_innovation_discovery_sync(input_bundle)
    except Exception as e:
        print(f"创新机会分析失败: {e}")
        return None

