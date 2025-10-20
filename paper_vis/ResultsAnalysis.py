"""
Results & Analysis部分JSON总结生成系统
从大段文本中动态提取3-5个关键点的JSON总结
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
USER_PROMPT_TEMPLATE = """Please execute your multi-step reasoning task for the **Results & Analysis** lane. Dynamically extract and summarize the core key points from the following section text.

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
    调用DeepSeek API分析文本并返回JSON格式的Results & Analysis总结
    
    Args:
        text: 要分析的文本内容
        max_retries: 最大重试次数，默认2次
        
    Returns:
        包含动态关键点的字典，如果失败返回None
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
                            if validate_results_json(json_result):
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

def validate_results_json(result: Dict[str, str]) -> bool:
    """
    验证Results & Analysis JSON结果是否符合要求
    
    Args:
        result: 要验证的结果
        
    Returns:
        是否符合要求
    """
    if not result:
        return False
    
    # 检查关键点数量（3-5个）
    key_count = len(result)
    if key_count < 3 or key_count > 5:
        print(f"关键点数量不符合要求: {key_count} (要求: 3-5个)")
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
        value_word_count = len(value.split())
        if value_word_count > 60:
            print(f"摘要超过60个单词限制: '{key}' ({value_word_count} 个单词)")
            return False
    
    return True

def analyze_results_analysis_sync(text: str, max_retries: int = MAX_RETRIES) -> Optional[Dict[str, str]]:
    """
    同步版本的Results & Analysis分析函数
    
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
    
    return validate_results_json(result)

# 示例使用
if __name__ == "__main__":
    # 示例文本1：深度学习实验结果
    sample_text_1 = """
    Our experimental results demonstrate significant improvements over baseline methods across multiple datasets. 
    On ImageNet, our model achieves 94.2% accuracy compared to 91.8% for ResNet-50 and 92.1% for EfficientNet-B0. 
    The attention mechanism contributes to a 2.4% performance boost, particularly in fine-grained classification tasks.
    
    Ablation studies reveal that removing the multi-head attention module reduces accuracy by 1.8%, while 
    disabling data augmentation decreases performance by 3.2%. Training time analysis shows our model converges 
    15% faster than baseline methods due to improved gradient flow.
    
    Cross-dataset evaluation on CIFAR-10 and CIFAR-100 confirms the generalizability of our approach, with 
    accuracy improvements of 1.9% and 2.3% respectively. Error analysis indicates that our model performs 
    particularly well on challenging samples with complex backgrounds and occlusions.
    """
    
    # 示例文本2：强化学习实验结果
    sample_text_2 = """
    The reinforcement learning experiments show substantial performance gains in navigation tasks. Our DQN-based 
    approach achieves 87% success rate compared to 45% for random policy and 62% for traditional Q-learning. 
    The experience replay mechanism reduces sample complexity by 40% while maintaining stable learning.
    
    Training convergence analysis reveals that our method reaches optimal performance after 50,000 episodes, 
    compared to 80,000 episodes for baseline methods. The epsilon-greedy exploration strategy with decay 
    proves crucial, contributing to 15% improvement in exploration efficiency.
    
    Robustness testing across different environments demonstrates consistent performance with success rates 
    ranging from 82% to 91%. The reward function design effectively balances goal-reaching behavior with 
    collision avoidance, resulting in 23% fewer collisions compared to baseline approaches.
    """
    
    # 示例文本3：自然语言处理实验结果
    sample_text_3 = """
    Sentiment analysis experiments demonstrate superior performance across multiple domains. Our BERT-based 
    model achieves 89.3% accuracy on Amazon reviews, 87.1% on Yelp, and 91.2% on IMDB datasets, outperforming 
    LSTM by 8.2% and CNN by 6.7% on average. The domain adaptation technique contributes to 3.4% improvement 
    in cross-domain performance.
    
    Fine-tuning analysis shows that our approach requires 30% fewer training epochs compared to vanilla BERT, 
    while achieving comparable performance. The adapter layer adds minimal computational overhead, increasing 
    inference time by only 5% while providing significant accuracy gains.
    
    Error analysis reveals that our model struggles most with sarcastic and ironic expressions, achieving 
    76% accuracy on such samples compared to 89% on straightforward sentiment expressions. However, 
    performance on neutral samples remains strong at 85% accuracy.
    """
    
    test_cases = [
        ("深度学习图像分类结果", sample_text_1),
        # ("强化学习机器人导航结果", sample_text_2),
        # ("自然语言处理情感分析结果", sample_text_3)
    ]
    
    for i, (description, text) in enumerate(test_cases, 1):
        print(f"=== 测试 {i}: {description} ===")
        print(f"输入文本长度: {len(text)} 字符")
        print()
        
        # 调用分析函数
        result = analyze_results_analysis_sync(text)
        
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
                    key_words = len(key.split())
                    value_words = len(value.split())
                    print(f"  '{key}' ({key_words} 词): {value_words} 个单词")
            else:
                print("✗ JSON格式验证失败")
        else:
            print("分析失败！")
        
        print("\n" + "="*60 + "\n")
   