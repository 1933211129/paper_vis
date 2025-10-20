# 学术论文智能分析API

基于 MainScheduler 的完整论文处理系统，提供PDF解析、泳道分析、摘要提取、图表映射等功能。

## 📡 API接口

### 核心接口

#### POST /paper_vis

分析PDF论文，返回MainScheduler的完整JSON结果。

**请求参数:**
```json
{
    "pdf_path": "/path/to/your/paper.pdf"
}
```

**响应示例:**

```json
{
    "success": true,
    "metadata": {
        "title": "HYPOSPACE: EVALUATING LLM CREATIVITY AS SET-VALUED HYPOTHESIS GENERATORS UNDER UNDERDETERMINATION",
        "authors": ["作者1", "作者2", "作者3"]
    },
    "abstract": {
        "background_problem": "背景和问题描述",
        "method_approach": "方法和途径", 
        "Innovation": "创新点",
        "Limitation/Future Work": "局限和未来工作"
    },
    "lanes": {
        "Context & Related Work": "相关工作和背景内容",
        "Methodology & Setup": "方法论和设置内容",
        "Results & Analysis": "结果和分析内容",
        "Conclusion": "结论内容",
        "Innovation Discovery": "学术创新机会发现"
    },
    "figure_map": {
        "Context & Related Work": [
            {
                "figure_id": "fig1",
                "caption": "图表标题",
                "content": "相关文本内容"
            }
        ],
        "Results & Analysis": [
            {
                "figure_id": "fig2", 
                "caption": "结果图表",
                "content": "结果相关文本"
            }
        ]
    },
    "pdf_info": {
        "file_path": "/path/to/paper.pdf",
        "file_size": 1234567,
        "page_count": 10
    },
    "processing_info": {
        "steps_completed": ["pdf_parsing", "abstract_steps", "lane_extraction", "figure_mapping", "final_json_generation"],
        "total_time": 22.54,
        "success": true
    },
    "raw_data": {
        "md_content_length": 50000,
        "content_list_count": 150,
        "figure_dict_count": 8
    }
}
```

### 辅助接口

#### GET /health

检查服务健康状态。

**响应:**
```json
{
    "status": "healthy",
    "timestamp": "2025-01-27T10:30:00Z"
}
```

#### GET /status

获取服务状态信息。

**响应:**

```json
{
    "status": "running",
    "uptime": 3600,
    "version": "1.0.0"
}
```

## 🧪 测试

### 使用curl测试

```bash
# 分析论文
curl -X POST "http://localhost:8004/paper_vis" \
     -H "Content-Type: application/json" \
     -d '{"pdf_path": "/path/to/your/paper.pdf"}'

# 检查健康状态
curl -X GET "http://localhost:8004/health"

# 获取服务状态
curl -X GET "http://localhost:8004/status"
```

### 使用Python requests

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试客户端
测试文件上传接口 /paper_vis
"""

import requests
import json
import time
import os


def test_paper_vis_upload():
    """测试 /paper_vis 文件上传接口"""
    
    # API服务器地址
    base_url = "http://10.3.35.21:8004"
    
    # 测试PDF文件路径
    test_pdf_path = "/Users/xiaokong/Desktop/2510.15614v1.pdf"
    
    print("🧪 测试 /paper_vis 文件上传接口")
    print("=" * 60)
    
    # 检查文件是否存在
    if not os.path.exists(test_pdf_path):
        print(f"❌ 测试文件不存在: {test_pdf_path}")
        return
    
    print(f"📄 上传文件: {test_pdf_path}")
    print("⏳ 开始分析...")
    
    start_time = time.time()
    
    try:
        # 准备文件上传
        with open(test_pdf_path, 'rb') as f:
            files = {
                'file': (os.path.basename(test_pdf_path), f, 'application/pdf')
            }
            
            response = requests.post(
                f"{base_url}/paper_vis",
                files=files,
                timeout=300  # 5分钟超时
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 论文分析成功")
            print(f"⏱️ 总耗时: {duration:.2f}秒")
            print(f"📊 处理结果:")
            print(f"   - 成功状态: {result.get('success', False)}")
            print(f"   - 处理时间: {result.get('total_time', 0):.2f}秒")
            
            if result.get('success'):
                print(f"   - 论文标题: {result.get('metadata', {}).get('title', 'N/A')}")
                authors = result.get('metadata', {}).get('authors', [])
                print(f"   - 作者数量: {len(authors) if authors else 0}")
                lanes = result.get('lanes', {})
                print(f"   - 泳道数量: {len(lanes) if lanes else 0}")
                figure_map = result.get('figure_map', {})
                total_figures = sum(len(figures) for figures in figure_map.values()) if figure_map else 0
                print(f"   - 图表总数: {total_figures}")
                
                # 保存结果到文件
                output_file = "paper_vis_upload_result.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"💾 结果已保存到: {output_file}")
            else:
                print(f"❌ 分析失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ 论文分析失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时（5分钟）")
    except Exception as e:
        print(f"❌ 论文分析异常: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")


def test_server_health():
    """测试服务器健康状态"""
    base_url = "http://10.3.35.21:8004"
    
    try:
        # 直接测试 /paper_vis 接口的OPTIONS请求
        response = requests.options(f"{base_url}/paper_vis", timeout=10)
        if response.status_code in [200, 405]:  # 405表示方法不允许，但接口存在
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False


if __name__ == "__main__":
    print("🚀 开始API测试")
    print("=" * 60)
    
    # 首先测试服务器健康状态
    if test_server_health():
        print("\n" + "=" * 60)
        # 测试文件上传接口
        test_paper_vis_upload()
    else:
        print("❌ 服务器不可用，请先启动API服务器")
        print("   运行命令: python api_server.py")
```

### 使用JavaScript

```javascript
/**
 * 论文分析API客户端
 * 对应Python版本的test_api_client.py
 */

const API_BASE_URL = "http://10.3.35.21:8004"

/**
 * 上传PDF文件并进行分析
 * @param {File} pdfFile - PDF文件对象
 * @param {Function} onProgress - 进度回调函数
 * @returns {Promise<Object>} 分析结果
 */
export async function analyzePaper(pdfFile, onProgress = null) {
  try {
    console.log('🚀 开始论文分析...')
    console.log('📄 文件信息:', {
      name: pdfFile.name,
      size: pdfFile.size,
      type: pdfFile.type
    })

    // 验证文件类型
    if (pdfFile.type !== 'application/pdf') {
      throw new Error('请选择PDF文件')
    }

    // 创建FormData
    const formData = new FormData()
    formData.append('file', pdfFile)

    // 显示进度
    if (onProgress) {
      onProgress(10, '准备上传文件...')
    }

    const startTime = Date.now()

    // 发送请求到 /paper_vis 接口
    const response = await fetch(`${API_BASE_URL}/paper_vis`, {
      method: 'POST',
      body: formData,
      // 注意：fetch不支持进度回调，这里我们模拟进度
    })

    const endTime = Date.now()
    const duration = (endTime - startTime) / 1000

    if (!response.ok) {
      throw new Error(`服务器错误: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()

    console.log('✅ 论文分析完成')
    console.log('⏱️ 总耗时:', duration.toFixed(2), '秒')
    console.log('📊 处理结果:', result)

    // 验证返回结果
    if (!result.success) {
      throw new Error(result.error || '分析失败')
    }

    // 显示最终进度
    if (onProgress) {
      onProgress(100, '分析完成！')
    }

    return {
      success: true,
      data: result,
      duration: duration,
      metadata: {
        title: result.metadata?.title || '未知标题',
        authors: result.metadata?.authors || [],
        totalTime: result.total_time || duration,
        lanesCount: Object.keys(result.lanes || {}).length,
        figuresCount: Object.values(result.figure_map || {}).reduce((total, figures) => total + figures.length, 0)
      }
    }

  } catch (error) {
    console.error('❌ 论文分析失败:', error)
    
    // 显示错误进度
    if (onProgress) {
      onProgress(0, `分析失败: ${error.message}`)
    }

    return {
      success: false,
      error: error.message,
      data: null
    }
  }
}

/**
 * 检查服务器健康状态
 * @returns {Promise<boolean>} 服务器是否可用
 */
export async function checkServerHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/paper_vis`, {
      method: 'OPTIONS',
      timeout: 10000
    })
    
    // 200或405都表示接口存在
    return response.status === 200 || response.status === 405
  } catch (error) {
    console.warn('服务器健康检查失败:', error)
    return false
  }
}

/**
 * 模拟进度更新（因为fetch不支持进度回调）
 * @param {Function} onProgress - 进度回调函数
 * @param {number} duration - 预计总时长（秒）
 */
export function simulateProgress(onProgress, duration = 30) {
  let progress = 0
  const interval = setInterval(() => {
    progress += Math.random() * 10
    if (progress >= 90) {
      progress = 90
      clearInterval(interval)
    }
    
    const statuses = [
      '正在上传文件...',
      'PDF解析中...',
      '内容抽取中...',
      '语义分析中...',
      '生成结果中...'
    ]
    
    const statusIndex = Math.floor((progress / 100) * statuses.length)
    const status = statuses[Math.min(statusIndex, statuses.length - 1)]
    
    onProgress(Math.floor(progress), status)
  }, 1000)

  return interval
}

```

### 错误处理示例

```python
import requests

try:
    response = requests.post(
        "http://localhost:8004/paper_vis",
        json={"pdf_path": "/path/to/your/paper.pdf"},
        timeout=300  # 5分钟超时
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ 论文分析成功")
            print(f"论文标题: {result['metadata']['title']}")
            print(f"处理时间: {result['processing_info']['total_time']}秒")
        else:
            print("❌ 论文分析失败")
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("❌ 请求超时，请稍后重试")
except requests.exceptions.ConnectionError:
    print("❌ 连接失败，请检查服务是否启动")
except Exception as e:
    print(f"❌ 未知错误: {e}")
```

## 📊 功能特性

- **PDF解析**: 自动解析PDF文件，提取文本和图表
- **泳道分析**: 按照学术论文结构提取五大泳道内容
- **摘要提取**: 智能提取四个摘要语步
- **图表映射**: 将图表按泳道分类并建立映射关系
- **元数据提取**: 自动提取论文标题、作者等信息
- **并行处理**: 多线程并行执行，提高处理效率
- **错误处理**: 完善的错误处理和状态监控
- **健康检查**: 内置健康状态检查接口

## 🔧 技术架构

- **后端框架**: FastAPI + Python 3.11+
- **核心引擎**: MainScheduler (综合调度器)
- **处理模块**: 
  - PDFParserClient (PDF解析)
  - AbstractSteps (摘要分析)
  - LaneExtractor (泳道提取)
  - FigureMapGenerator (图表映射)
- **并发处理**: ThreadPoolExecutor (多线程并行)
- **服务端口**: 8004
- **超时设置**: 300秒 (5分钟)

## 📈 性能指标

- **处理时间**: 通常 20-30 秒 (取决于论文长度)
- **并发能力**: 支持多线程并行处理
- **内存使用**: 优化内存使用，支持大文件处理
- **错误恢复**: 自动错误检测和恢复机制

## 🚨 注意事项

1. **文件路径**: 确保PDF文件路径正确且可访问

2. **处理时间**: 大型论文可能需要较长时间处理

3. **文件格式**: 仅支持标准PDF格式

   
