"""
Context & Related Work部分JSON总结生成系统
从大段文本中提取四个固定关键点的JSON总结
"""

import asyncio
import aiohttp
import json
import time
from typing import Optional, Dict, Any
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, DEEPSEEK_MODEL, MAX_RETRIES, MAX_TOKENS, TEMPERATURE

# DeepSeek API配置
API_KEY = DEEPSEEK_API_KEY
API_URL = DEEPSEEK_API_URL
MODEL = DEEPSEEK_MODEL

# 系统提示词
SYSTEM_PROMPT = """You are a highly specialized cross-disciplinary academic structure analyst. Your sole mission is to execute an advanced multi-step reasoning task:

1.  **Context Analysis:** Infer the paper's **precise discipline** and **research focus** entirely from the provided **section text**.
2.  **Dynamic Design:** Based on the inference, dynamically design the most representative **Key Points** for the target lane and create a concise title for each.
3.  **Content Extraction:** Extract the most accurate summary for each dynamically designed key point from the provided text.

**[Extraction Constraints]**
1.  **Quantity Limit:** The number of key points MUST be between **3 and 5** (inclusive).
2.  **Title Limit:** The Key (Title) for each point MUST be concise, using **no more than 4 English words**.
3.  **Summary Limit:** The Value (Summary) MUST be in **English** and must not exceed **60 English words**, focusing on high-level generalization.

**[Format Requirement]**
1.  You MUST output a single, strictly valid **JSON object**.
2.  You MUST NOT output any explanation, prelude, or text outside of the raw JSON object.
3.  If a summary cannot be extracted, output **"N/A"** as the value for that key."""

# 用户提示词模板
USER_PROMPT_TEMPLATE = """Please execute your multi-step reasoning task for the **Context & Related Work** lane. Dynamically extract and summarize the core key points from the following section text.

**[Section Text for Extraction]**
// The LLM must infer the domain and focus from this text alone.
{text}

**[Expected JSON Structure Example]**
Strictly output your result as a concise key-value JSON object:

{{
  "Dynamic Title 1": "The English summary corresponding to this title, not exceeding 60 words.",
  "Dynamic Title 2": "The English summary corresponding to this title, not exceeding 60 words.",
  "Dynamic Title 3": "The English summary corresponding to this title, not exceeding 60 words."
  // ... maximum of 5 keys
}}"""

async def call_deepseek_api(text: str, max_retries: int = MAX_RETRIES) -> Optional[Dict[str, str]]:
    """
    调用DeepSeek API分析文本并返回JSON格式的Context & Related Work总结
    
    Args:
        text: 要分析的文本内容
        max_retries: 最大重试次数，默认2次
        
    Returns:
        包含四个关键点的字典，如果失败返回None
    """
    user_prompt = USER_PROMPT_TEMPLATE.format(text=text)
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    for attempt in range(max_retries + 1):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content'].strip()
                        
                        # 尝试解析JSON
                        try:
                            # 清理可能的markdown代码块标记
                            if content.startswith('```json'):
                                content = content[7:]
                            if content.endswith('```'):
                                content = content[:-3]
                            content = content.strip()
                            
                            json_result = json.loads(content)
                            
                            # 验证JSON结构
                            if validate_context_json(json_result):
                                return json_result
                            else:
                                print(f"警告：JSON结构不符合要求，尝试 {attempt + 1}/{max_retries + 1}")
                                if attempt < max_retries:
                                    await asyncio.sleep(1)
                                    continue
                                
                        except json.JSONDecodeError as e:
                            print(f"JSON解析失败，尝试 {attempt + 1}/{max_retries + 1}: {e}")
                            print(f"原始响应: {content}")
                            if attempt < max_retries:
                                await asyncio.sleep(1)
                                continue
                    else:
                        print(f"API请求失败，状态码: {response.status}")
                        if attempt < max_retries:
                            await asyncio.sleep(2)
                            continue
                            
        except Exception as e:
            print(f"请求异常，尝试 {attempt + 1}/{max_retries + 1}: {e}")
            if attempt < max_retries:
                await asyncio.sleep(2)
                continue
    
    print("所有重试尝试均失败")
    return None

def analyze_context_related_work_sync(text: str, max_retries: int = MAX_RETRIES) -> Optional[Dict[str, str]]:
    """
    同步版本的Context & Related Work分析函数
    
    Args:
        text: 要分析的文本内容
        max_retries: 最大重试次数，默认2次
        
    Returns:
        包含动态关键点的字典，如果失败返回None
    """
    try:
        return asyncio.run(call_deepseek_api(text, max_retries))
    except Exception as e:
        print(f"同步调用失败: {e}")
        return None

def validate_context_json(result: Dict[str, str]) -> bool:
    """
    验证Context & Related Work JSON结果是否符合要求
    
    Args:
        result: 要验证的结果
        
    Returns:
        是否符合要求
    """
    if not result:
        return False
    
    # 检查关键点数量（3-5个）
    if len(result) < 3 or len(result) > 5:
        print(f"关键点数量不符合要求: {len(result)} (要求: 3-5个)")
        return False
    
    # 检查每个字段的值
    for key, value in result.items():
        if not isinstance(value, str):
            return False
        
        # 检查标题长度（不超过4个英文单词）
        key_word_count = len(key.split())
        if key_word_count > 4:
            print(f"标题超过4个单词限制: '{key}' ({key_word_count} 个单词)")
            return False
        
        # 检查摘要长度（不超过60个英文单词）
        if value != "N/A":
            value_word_count = len(value.split())
            if value_word_count > 60:
                print(f"摘要超过60个单词限制: '{key}' ({value_word_count} 个单词)")
                return False
    
    return True

def validate_json_output(result: Optional[Dict[str, str]]) -> bool:
    """
    验证返回的JSON结果是否符合要求
    
    Args:
        result: 要验证的结果
        
    Returns:
        是否符合要求
    """
    if not result:
        return False
    
    return validate_context_json(result)

# 示例使用
if __name__ == "__main__":
    # 示例文本
    sample_text = """
    Reinforcement learning has emerged as a powerful paradigm for enabling autonomous behavior in robots. 
    However, training RL agents in real-world environments presents significant challenges including safety concerns, 
    high costs, and time constraints. The sparse reward problem and the simulation-to-reality gap further 
    complicate the application of RL to robotic systems. Previous work has focused on simulation-based training 
    with domain adaptation techniques, but these approaches often fail to capture the full complexity of real-world dynamics.
    
    The inverted pendulum balancing problem serves as a classic benchmark for continuous control tasks. 
    Traditional control methods like PID controllers have been widely used, but they require manual tuning 
    and may not adapt well to changing conditions. Recent advances in deep reinforcement learning have shown 
    promise for learning control policies directly from interaction with the environment.
    
    This work addresses the challenge of applying Q-learning to continuous control problems by discretizing 
    the action space and using a carefully designed reward function. The main contribution is demonstrating 
    that a simple Q-learning approach can successfully learn to balance an inverted pendulum and transfer 
    the learned policy to a real robot system.
    """
    
    print("=== Context & Related Work 分析测试 ===")
    result = analyze_context_related_work_sync(sample_text)
    
    if result:
        print("分析成功！")
        print("JSON结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 验证结果
        if validate_json_output(result):
            print("\n✓ JSON格式验证通过")
        else:
            print("\n✗ JSON格式验证失败")
    else:
        print("分析失败！")
