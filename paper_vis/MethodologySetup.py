"""
Methodology & Setup部分JSON总结生成系统
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
USER_PROMPT_TEMPLATE = """Please execute your multi-step reasoning task for the **Methodology & Setup** lane. Dynamically extract and summarize the core key points from the following section text.

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
    调用DeepSeek API分析文本并返回JSON格式的Methodology & Setup总结
    
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
                            if validate_methodology_json(json_result):
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

def validate_methodology_json(result: Dict[str, str]) -> bool:
    """
    验证Methodology & Setup JSON结果是否符合要求
    
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

def analyze_methodology_setup_sync(text: str, max_retries: int = MAX_RETRIES) -> Optional[Dict[str, str]]:
    """
    同步版本的Methodology & Setup分析函数
    
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
    
    return validate_methodology_json(result)

# 示例使用
if __name__ == "__main__":
    # 示例文本1：深度学习相关
    sample_text_1 = """
    We propose a novel deep learning architecture for image classification that combines convolutional neural networks 
    with attention mechanisms. Our model consists of three main components: a feature extraction backbone using ResNet-50, 
    a multi-head attention module for capturing spatial dependencies, and a classification head with dropout regularization.
    
    The training process involves two phases: pre-training on ImageNet dataset and fine-tuning on our target dataset. 
    We use Adam optimizer with learning rate scheduling, batch size of 32, and early stopping to prevent overfitting. 
    Data augmentation techniques include random rotation, horizontal flipping, and color jittering.
    
    For evaluation, we employ 5-fold cross-validation and report accuracy, precision, recall, and F1-score metrics. 
    The experiments are conducted on NVIDIA V100 GPUs with PyTorch framework. We compare our approach against 
    baseline methods including VGG-16, ResNet-50, and EfficientNet-B0.
    """
    
    # 示例文本2：强化学习相关
    sample_text_2 = """
    Our reinforcement learning framework employs Deep Q-Network (DQN) with experience replay and target network updates. 
    The state space consists of continuous sensor readings from the robot's environment, while the action space is 
    discretized into 8 possible movements. We use a neural network with two hidden layers of 128 neurons each.
    
    The reward function is designed to encourage goal-reaching behavior while penalizing collisions and excessive 
    energy consumption. Training is performed using epsilon-greedy exploration with decaying epsilon from 1.0 to 0.1. 
    The experience replay buffer stores 10,000 transitions with uniform sampling.
    
    Simulation experiments are conducted in Gazebo environment with TurtleBot3 robot. We evaluate performance using 
    success rate, path length, and training time metrics. The baseline comparison includes random policy, 
    traditional Q-learning, and policy gradient methods.
    """
    
    test_cases = [
        ("深度学习图像分类", sample_text_1),
        # ("强化学习机器人导航", sample_text_2)
    ]
    
    for i, (description, text) in enumerate(test_cases, 1):
        print(f"=== 测试 {i}: {description} ===")
        print(f"输入文本长度: {len(text)} 字符")
        print()
        
        # 调用分析函数
        result = analyze_methodology_setup_sync(text)
        
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
