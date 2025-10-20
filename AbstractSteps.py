"""
学术摘要语步提取系统
从Markdown文件中提取摘要并分析其四步语步结构
"""

import asyncio
import aiohttp
import json
import os
from typing import Optional
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL, MAX_RETRIES, MAX_TOKENS, TEMPERATURE
from pathlib import Path

# DeepSeek API配置
API_KEY = DEEPSEEK_API_KEY
API_URL = DEEPSEEK_API_URL
MODEL = DEEPSEEK_MODEL

# 注意：不再使用Pydantic模型，直接返回JSON格式的列表

# 系统提示词
SYSTEM_PROMPT = """You are a highly specialized expert in academic text analysis and structured data extraction. Your **sole task** is to analyze the provided academic text and extract three key pieces of information, outputting the result in a **strictly valid JSON array format**.

**[Core Task & Output]**
1. Analyze the provided text (first 5000 characters of an academic paper)
2. Extract the paper title, abstract rhetorical steps, and author list
3. Output the result as a JSON array with exactly 3 elements

**[Required Output Format]**
You **MUST** output a JSON array with exactly 3 elements in this exact order:
[
    "Paper Title",
    ["Author1", "Author2", "Author3"],
    {
        "Background/Problem": "The concise English summary for this step, no more than 35 words.",
        "Method/Approach": "The concise English summary for this step, no more than 35 words.",
        "Innovation": "The concise English summary for this step, no more than 35 words.",
        "Limitation/Future Work": "The concise English summary for this step, no more than 35 words."
    }
]

**[Critical Requirements]**
1. **MUST** output a JSON array with exactly 3 elements
2. **ABSOLUTELY DO NOT** output any introductory text, explanations, or text outside the raw JSON array
3. First element: Paper title as a string
4. Second element: Abstract steps as a JSON object with 4 required fields
5. Third element: Author list as an array of strings (empty array [] if no authors found)
6. Each abstract step summary **MUST NOT exceed 35 English words**"""

# 用户提示词模板
USER_PROMPT_TEMPLATE = """Please analyze the academic text provided below and extract the paper title, abstract rhetorical steps, and author list.

**[Text to Analyze]**
{text}

**[Required Output Format]**
You **MUST** output a JSON array with exactly 3 elements in this exact order:

[
    "Paper Title",
    ["Author1", "Author2", "Author3"],
    {{
        "Background/Problem": "The concise English summary for this step, no more than 35 words.",
        "Method/Approach": "The concise English summary for this step, no more than 35 words.",
        "Innovation": "The concise English summary for this step, no more than 35 words.",
        "Limitation/Future Work": "The concise English summary for this step, no more than 35 words."
    }}
]

**Important Notes:**
- If no authors are found, use an empty array: []
- Each abstract step must not exceed 35 English words
- Output ONLY the JSON array, no other text"""

def extract_text_for_llm(md_content: str) -> str:
    """
    从markdown内容中提取前5000个字符用于LLM分析
    
    Args:
        md_content: markdown内容字符串
    
    Returns:
        str: 前5000个字符的文本
    """
    try:
        # 取前5000字符
        text_for_llm = md_content[:5000]
        return text_for_llm
            
    except Exception as e:
        return ""

async def call_deepseek_api(text: str, max_retries: int = MAX_RETRIES) -> Optional[list]:
    """
    调用DeepSeek API进行学术文本分析
    
    Args:
        text: 要分析的文本
        max_retries: 最大重试次数
    
    Returns:
        list: [标题, 作者列表, 摘要语步JSON] 或 None
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    user_prompt = USER_PROMPT_TEMPLATE.format(text=text)
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 800,
        "temperature": TEMPERATURE  # 降低随机性，提高一致性
    }
    
    for attempt in range(max_retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, json=payload, headers=headers) as response:
                    if response.status != 200:
                        if attempt < max_retries:
                            await asyncio.sleep(1)  # 等待1秒后重试
                            continue
                        return None
                    
                    result = await response.json()
                    
                    # 提取回复内容
                    if "choices" in result and len(result["choices"]) > 0:
                        content = result["choices"][0]["message"]["content"].strip()
                        
                        # 尝试解析JSON
                        try:
                            # 清理可能的markdown代码块标记
                            if content.startswith("```json"):
                                content = content[7:]
                            if content.endswith("```"):
                                content = content[:-3]
                            content = content.strip()
                            
                            # 解析JSON数组
                            json_data = json.loads(content)
                            
                            # 验证返回的是列表且包含3个元素
                            if isinstance(json_data, list) and len(json_data) == 3:
                                return json_data
                            else:
                                if attempt < max_retries:
                                    await asyncio.sleep(1)
                                    continue
                            
                        except json.JSONDecodeError as e:
                            if attempt < max_retries:
                                await asyncio.sleep(1)
                                continue
                            
                        except Exception as e:
                            if attempt < max_retries:
                                await asyncio.sleep(1)
                                continue
                    else:
                        if attempt < max_retries:
                            await asyncio.sleep(1)
                            continue
                        
        except Exception as e:
            if attempt < max_retries:
                await asyncio.sleep(1)
                continue
    
    return None

async def analyze_abstract_steps(md_content: str) -> Optional[list]:
    """
    分析markdown内容的学术信息
    
    Args:
        md_content: markdown内容字符串
    
    Returns:
        list: [标题, 作者列表, 摘要语步JSON] 或 None
    """
    # 1. 提取分析文本（前5000字符）
    analysis_text = extract_text_for_llm(md_content)
    
    if not analysis_text.strip():
        return None
    
    # 2. 调用LLM分析
    result = await call_deepseek_api(analysis_text)
    
    return result

def analyze_abstract_steps_sync(md_content: str) -> Optional[list]:
    """
    同步版本的学术信息分析函数，供外部应用调用
    
    Args:
        md_content: markdown内容字符串
    
    Returns:
        list: [标题, 作者列表, 摘要语步JSON] 或 None
        格式: ["Paper Title", ["Author1", "Author2"], {"Background/Problem": "...", "Method/Approach": "...", "Result": "...", "Conclusion/Contribution": "..."}]
        如果分析失败返回None
    """
    try:
        # 运行异步分析
        result = asyncio.run(analyze_abstract_steps(md_content))
        return result
            
    except Exception as e:
        return None


def analyze_abstract_steps_from_content(md_content: str) -> Optional[dict]:
    """
    从markdown内容分析学术信息并返回JSON对象
    
    Args:
        md_content: markdown内容字符串
    
    Returns:
        dict: 包含abstract和metadata的JSON对象，格式如下：
        {
            "abstract": {
                "Background/Problem": "...",
                "Method/Approach": "...",
                "Result": "...",
                "Conclusion/Contribution": "..."
            },
            "metadata": {
                "title": "Paper Title",
                "authors": ["Author1", "Author2"]
            }
        }
        如果分析失败返回None
    """
    try:
        # 分析摘要语步
        result = analyze_abstract_steps_sync(md_content)
        
        if not result or len(result) != 3:
            return None
        
        paper_title, author_list, abstract_steps = result
        
        # 构建返回的JSON对象
        return {
            "abstract": abstract_steps,
            "metadata": {
                "title": paper_title,
                "authors": author_list
            }
        }
        
    except Exception as e:
        return None

# 运行测试
if __name__ == "__main__":
    # 示例用法
    sample_md_content = """
    # Sample Paper Title
    
    ## Abstract
    This is a sample abstract with background, method, results, and conclusion.
    """
    
    result = analyze_abstract_steps_from_content(sample_md_content)
    print(result)