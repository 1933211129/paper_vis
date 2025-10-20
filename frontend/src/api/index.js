// API服务文件
const API_BASE_URL = 'http://localhost:8000'

// 上传PDF文件
export async function uploadPdf(formData, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    
    // 监听上传进度
    if (onProgress) {
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100)
          onProgress(progress)
        }
      })
    }
    
    // 监听请求完成
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const result = JSON.parse(xhr.responseText)
          resolve({ data: result })
        } catch (error) {
          reject(new Error('Invalid JSON response'))
        }
      } else {
        reject(new Error(`HTTP error! status: ${xhr.status}`))
      }
    })
    
    // 监听请求错误
    xhr.addEventListener('error', () => {
      reject(new Error('Network error'))
    })
    
    // 发送请求
    xhr.open('POST', `${API_BASE_URL}/upload`)
    xhr.send(formData)
  })
}

// 开始分析
export async function startAnalysis(folderId) {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ folder_id: folderId })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const result = await response.json()
    return { data: result }
  } catch (error) {
    console.error('Analysis failed:', error)
    throw error
  }
}
