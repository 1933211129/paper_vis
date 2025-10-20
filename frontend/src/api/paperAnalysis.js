/**
 * 论文分析API客户端
 * 对应Python版本的test_api_client.py
 */

// API基础URL - 使用代理路径避免CORS问题
const API_BASE_URL = process.env.NODE_ENV === 'development' ? '/api' : 'http://10.3.35.21:8004'

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
      mode: 'cors', // 明确指定CORS模式
      headers: {
        // 不设置Content-Type，让浏览器自动设置multipart/form-data
      },
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
    
    // 检查是否是CORS错误
    let errorMessage = error.message || '未知错误'
    if (error.message.includes('CORS') || error.message.includes('Failed to fetch')) {
      errorMessage = '跨域请求被阻止，请检查后端服务器CORS配置或使用代理'
    }
    
    // 显示错误进度
    if (onProgress) {
      onProgress(0, `分析失败: ${errorMessage}`)
    }

    return {
      success: false,
      error: errorMessage,
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
export function simulateProgress(onProgress) {
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
