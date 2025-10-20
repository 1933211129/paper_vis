# 标题映射LLM模块

这是一个利用大语言模型(LLM)对学术论文章节标题进行分类映射的Python模块。该模块可以将论文的标题列表自动分类到四个标准的研究泳道中。

## 功能特性

- 🎯 **智能分类**: 利用LLM将论文章节标题映射到四个标准泳道
- 🔍 **噪声过滤**: 自动过滤非章节内容（如作者信息、参考文献等）
- 📊 **配额限制**: 每个泳道最多映射2个标题，确保核心内容突出
- 🛡️ **错误处理**: 完善的错误处理和重试机制
- 🔧 **调试支持**: 提供详细的调试信息
- 🌐 **API兼容**: 支持OpenAI API及兼容格式的其他LLM服务

## 四个标准泳道

1. **Context & Related Work** - 背景与相关工作
2. **Methodology & Setup** - 方法论与设置  
3. **Results & Analysis** - 结果与分析
4. **Conclusion** - 结论

## 安装依赖

```bash
pip install requests
```

## 快速开始

### 基本使用

```python
from TitleMappingLLM import TitleMappingLLM

# 1. 初始化映射器
mapper = TitleMappingLLM(
    api_key="your-openai-api-key",  # 替换为你的API密钥
    model="gpt-3.5-turbo"
)

# 2. 准备标题列表
title_list = [
    "# Deep Learning for Medical Image Analysis",
    "# Abstract",
    "# 1. Introduction",
    "# 2. Related Work", 
    "# 3. Methodology",
    "# 4. Results",
    "# 5. Conclusion",
    "# References"
]

# 3. 执行映射
result = mapper.map_titles(title_list)

# 4. 处理结果
if result['success']:
    print("映射成功！")
    print(result['result'])
else:
    print(f"映射失败: {result['error']}")
```

### 调试模式

```python
# 获取详细的调试信息
debug_result = mapper.map_titles_with_debug(title_list)
print(f"调试信息: {debug_result['debug_info']}")
```

## API参考

### TitleMappingLLM类

#### 初始化参数

- `api_url` (str, 可选): LLM API地址，默认为OpenAI API
- `api_key` (str, 必需): API密钥
- `model` (str, 可选): 使用的模型名称，默认为"gpt-3.5-turbo"

#### 主要方法

##### `map_titles(title_list: List[str]) -> Dict[str, Any]`

将标题列表映射到四个标准泳道。

**参数:**
- `title_list`: 原始标题列表

**返回值:**
```python
{
    "success": bool,           # 是否成功
    "error": str,             # 错误信息（如果失败）
    "result": {               # 映射结果（如果成功）
        "Context & Related Work": ["标题1", "标题2"],
        "Methodology & Setup": ["标题1"],
        "Results & Analysis": ["标题1"],
        "Conclusion": ["标题1"]
    },
    "statistics": {           # 统计信息
        "total_input_titles": int,
        "total_mapped_titles": int,
        "mapping_distribution": {...}
    }
}
```

##### `map_titles_with_debug(title_list: List[str]) -> Dict[str, Any]`

带调试信息的标题映射，包含额外的调试信息。

## 使用示例

### 示例1: 简单映射

```python
from TitleMappingLLM import TitleMappingLLM

mapper = TitleMappingLLM(api_key="your-key")
titles = ["# Introduction", "# Methods", "# Results", "# Conclusion"]
result = mapper.map_titles(titles)

if result['success']:
    for lane, mapped_titles in result['result'].items():
        print(f"{lane}: {mapped_titles}")
```

### 示例2: 批量处理

```python
papers = [
    {"id": "paper1", "titles": ["# Intro", "# Methods", "# Results"]},
    {"id": "paper2", "titles": ["# Background", "# Approach", "# Analysis"]}
]

mapper = TitleMappingLLM(api_key="your-key")
results = {}

for paper in papers:
    result = mapper.map_titles(paper['titles'])
    if result['success']:
        results[paper['id']] = result['result']
```

### 示例3: 错误处理

```python
result = mapper.map_titles(title_list)

if not result['success']:
    error = result['error']
    if "API" in error:
        print("API调用失败，请检查密钥和网络")
    elif "解析" in error:
        print("响应解析失败，请检查LLM输出格式")
    else:
        print(f"其他错误: {error}")
```

## 支持的LLM服务

- ✅ OpenAI GPT (gpt-3.5-turbo, gpt-4等)
- ✅ 兼容OpenAI API格式的其他服务
- ✅ 自定义API端点

## 注意事项

1. **API密钥**: 确保设置有效的API密钥
2. **网络连接**: 需要稳定的网络连接访问LLM API
3. **标题格式**: 标题列表应包含完整的标题字符串
4. **配额限制**: 每个泳道最多映射2个标题
5. **错误处理**: 建议在生产环境中添加适当的错误处理逻辑

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 验证API端点地址

2. **JSON解析失败**
   - LLM响应格式可能不符合预期
   - 检查模型参数设置
   - 使用调试模式查看原始响应

3. **映射结果不准确**
   - 调整模型温度参数
   - 检查标题列表质量
   - 考虑使用更高级的模型

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个模块。
