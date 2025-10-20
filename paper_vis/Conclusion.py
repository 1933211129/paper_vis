"""
Conclusion部分JSON总结生成系统
从大段文本中提取4个固定关键点的JSON总结
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
USER_PROMPT_TEMPLATE = """Please execute your multi-step reasoning task for the **Conclusion** lane. Dynamically extract and summarize the core key points from the following section text.

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
    调用DeepSeek API分析文本并返回JSON格式的Conclusion总结
    
    Args:
        text: 要分析的文本内容
        max_retries: 最大重试次数，默认2次
        
    Returns:
        包含4个固定关键点的字典，如果失败返回None
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
                            if validate_conclusion_json(json_result):
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

def validate_conclusion_json(result: Dict[str, str]) -> bool:
    """
    验证Conclusion JSON结果是否符合要求
    
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

def analyze_conclusion_sync(text: str, max_retries: int = MAX_RETRIES) -> Optional[Dict[str, str]]:
    """
    同步版本的Conclusion分析函数
    
    Args:
        text: 要分析的文本内容
        max_retries: 最大重试次数，默认2次
        
    Returns:
        包含4个固定关键点的字典，如果失败返回None
    """
    try:
        return asyncio.run(call_deepseek_api(text, max_retries))
    except Exception as e:
        print(f"同步调用失败: {e}")
        return None

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
    
    return validate_conclusion_json(result)

# 示例使用
if __name__ == "__main__":
    # 示例文本1：深度学习论文结论
    sample_text_1 = """
    In this paper, we presented a novel deep learning architecture that combines convolutional neural networks 
    with attention mechanisms for image classification tasks. Our main contributions include: (1) a multi-head 
    attention module that captures spatial dependencies in feature maps, (2) an efficient training strategy 
    that reduces convergence time by 15%, and (3) comprehensive experiments demonstrating superior performance 
    on multiple datasets including ImageNet, CIFAR-10, and CIFAR-100.
    
    Despite these achievements, our work has several limitations. The model requires significant computational 
    resources during training, making it challenging to deploy on resource-constrained devices. Additionally, 
    the attention mechanism increases model complexity and inference time compared to standard CNNs. The evaluation 
    was primarily conducted on natural images, and the model's performance on medical or satellite imagery 
    remains unexplored.
    
    Future research directions include investigating lightweight attention mechanisms for mobile deployment, 
    extending the architecture to handle multi-modal inputs, and exploring self-supervised learning approaches 
    to reduce the need for large labeled datasets. We also plan to investigate the interpretability of attention 
    weights to better understand what the model learns.
    
    The practical implications of this work extend to various computer vision applications including autonomous 
    vehicles, medical imaging, and surveillance systems. The improved accuracy and faster convergence could 
    significantly reduce training costs and improve real-world deployment efficiency. This research contributes 
    to the broader goal of developing more efficient and accurate deep learning models for computer vision tasks.
    """
    
    # 示例文本2：自然语言处理论文结论
    sample_text_2 = """
    This paper introduced a new approach to sentiment analysis using transformer-based models with domain 
    adaptation techniques. Our key contributions are: (1) a novel domain adaptation framework that improves 
    cross-domain performance by 3.4%, (2) an efficient fine-tuning strategy that reduces training time by 30%, 
    and (3) comprehensive evaluation across multiple domains including product reviews, social media, and news articles.
    
    The limitations of our approach include its sensitivity to sarcastic and ironic expressions, where performance 
    drops to 76% accuracy. The model also requires domain-specific labeled data for effective adaptation, which 
    may not always be available. Additionally, the computational overhead of the adapter layers, while minimal, 
    still adds 5% to inference time.
    
    Future work will focus on developing more robust models for handling figurative language and sarcasm. 
    We plan to investigate few-shot learning approaches to reduce the dependency on large labeled datasets. 
    Another direction is exploring multi-task learning to simultaneously handle sentiment analysis and other 
    related tasks like emotion detection and aspect-based sentiment analysis.
    
    This research has practical implications for businesses and organizations that rely on sentiment analysis 
    for decision-making. The improved cross-domain performance enables more reliable analysis across different 
    platforms and contexts. The reduced training time makes it more feasible for organizations to deploy 
    customized sentiment analysis models for their specific needs.
    """
    
    # 示例文本3：强化学习论文结论
    sample_text_3 = """
    We proposed a novel deep Q-network architecture for autonomous navigation tasks with improved exploration 
    strategies. Our main contributions include: (1) an enhanced experience replay mechanism that reduces 
    sample complexity by 40%, (2) an adaptive epsilon-greedy exploration strategy that improves exploration 
    efficiency by 15%, and (3) a reward function design that balances goal-reaching behavior with collision 
    avoidance, resulting in 23% fewer collisions.
    
    Several limitations remain in our current approach. The training process still requires a substantial 
    number of episodes (50,000) to reach optimal performance, which may be impractical for real-world 
    applications with limited training time. The reward function design is task-specific and may not generalize 
    well to other navigation scenarios. Additionally, the evaluation was conducted in simulated environments, 
    and the transfer to real robots remains to be validated.
    
    Future research directions include developing more sample-efficient learning algorithms, investigating 
    transfer learning approaches for faster adaptation to new environments, and exploring multi-agent scenarios 
    where multiple robots navigate simultaneously. We also plan to investigate the integration of our approach 
    with model-based reinforcement learning methods to further improve sample efficiency.
    
    The practical impact of this work extends to robotics applications including warehouse automation, 
    autonomous vehicles, and service robots. The improved navigation performance and reduced collision rates 
    could significantly enhance safety and efficiency in these applications. This research contributes to 
    the development of more reliable and efficient autonomous navigation systems.
    """
    
    test_cases = [
        ("深度学习图像分类结论", sample_text_1),
        # ("自然语言处理情感分析结论", sample_text_2),
        # ("强化学习机器人导航结论", sample_text_3)
    ]
    
    for i, (description, text) in enumerate(test_cases, 1):
        print(f"=== 测试 {i}: {description} ===")
        print(f"输入文本长度: {len(text)} 字符")
        print()
        
        # 调用分析函数
        result = analyze_conclusion_sync(text)
        
        if result:
            print("分析成功！")
            print("JSON结果:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print()
            
            # 验证结果
            if validate_json_output(result):
                print("✓ JSON格式验证通过")
                
                # 显示统计信息
                print(f"\n关键点数量: {len(result)}")
                print("字数统计:")
                for key, value in result.items():
                    value_words = len(value.split()) if value != "N/A" else 0
                    print(f"  '{key}': {value_words} 个单词")
            else:
                print("✗ JSON格式验证失败")
        else:
            print("分析失败！")
        
        print("\n" + "="*60 + "\n")
