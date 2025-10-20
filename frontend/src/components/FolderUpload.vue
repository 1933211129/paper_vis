<template>
  <div class="single-page">
    <!-- 背景 -->
    <div class="page-background">
      <div class="background-particles"></div>
    </div>
    
    <!-- 主内容区域 -->
    <div class="main-container">
      <!-- 左侧：系统介绍 -->
      <div class="left-panel">
        <!-- 标题区域 -->
        <div class="title-section">
          <div class="system-badge">
            <span class="badge-icon">🚀</span>
            <span>基于大语言模型的智能分析系统</span>
          </div>
          <h1 class="main-title">
            学术论文
            <span class="gradient-text">智能分析</span>
            系统
          </h1>
          <p class="main-description">
            自动解析学术论文内容，提取关键信息，生成结构化数据
            <br>支持摘要语步分析、内容分区划分、图表映射等核心功能
          </p>
        </div>
        
        <!-- 核心功能 -->
        <div class="features-section">
          <h3 class="section-title">核心功能</h3>
          <div class="features-grid">
            <div class="feature-item" v-for="feature in features" :key="feature.id">
              <div class="feature-icon">{{ feature.icon }}</div>
              <div class="feature-content">
                <h4 class="feature-title">{{ feature.title }}</h4>
                <p class="feature-desc">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 数据统计 -->
        <div class="stats-section">
          <div class="stat-item">
            <div class="stat-number">9</div>
            <div class="stat-label">标准化输出对象</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">5</div>
            <div class="stat-label">内容分区分析</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">∞</div>
            <div class="stat-label">并发处理能力</div>
          </div>
        </div>
      </div>
      
      <!-- 右侧：上传区域 -->
      <div class="right-panel">
        <div class="upload-container">
          <div class="upload-header">
            <h2 class="upload-title">开始分析</h2>
            <p class="upload-subtitle">上传您的PDF论文文件，开始智能分析之旅</p>
          </div>
          
          <!-- PDF文件选择区域 -->
          <div class="upload-area" :class="{ 'dragover': isDragOver }" 
               @drop="handleDrop" 
               @dragover.prevent="isDragOver = true"
               @dragleave="isDragOver = false"
               @click="triggerFileInput">
            <div class="upload-content">
              <div class="upload-icon">📄</div>
              <h3>选择PDF论文文件</h3>
              <p>点击选择或拖拽PDF文件到此处</p>
              <div class="file-requirements">
                <div class="requirement-title">支持的文件格式：</div>
                <div class="requirement-list">
                  <div class="requirement-item">
                    <span class="file-icon">📄</span>
                    <span>PDF 文件</span>
                  </div>
                  <div class="requirement-item">
                    <span class="file-icon">🔍</span>
                    <span>自动解析内容</span>
                  </div>
                  <div class="requirement-item">
                    <span class="file-icon">📊</span>
                    <span>智能分析</span>
                  </div>
                  <div class="requirement-item">
                    <span class="file-icon">⚡</span>
                    <span>快速处理</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 隐藏的文件输入 -->
          <input 
            ref="fileInput" 
            type="file" 
            accept=".pdf"
            @change="handleFileSelect"
            style="display: none;">
          
          <!-- 上传进度 -->
          <div v-if="uploading" class="upload-progress">
            <div class="progress-header">
              <h4>📤 总体进度...</h4>
              <span class="progress-text">{{ uploadProgress.toFixed(2) }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
            </div>
            <p class="progress-detail">{{ uploadStatus }}</p>
          </div>
          
          <!-- 上传结果 - 简化为1秒提示 -->
          <div v-if="uploadResult" class="upload-result-simple" :class="uploadResult.success ? 'success' : 'error'">
            <div class="result-icon">{{ uploadResult.success ? '✅' : '❌' }}</div>
            <span>{{ uploadResult.success ? '分析成功！' : '上传失败' }}</span>
          </div>
          
          <!-- PDF解析进度 -->
          <div v-if="parsingProgress" class="parsing-progress">
            <div class="progress-spinner"></div>
            <h4>📄 PDF解析中...</h4>
            <p class="progress-text">{{ parsingStatus }}</p>
          </div>
          
          <!-- 内容抽取进度 -->
          <div v-if="extractionProgress" class="extraction-progress">
            <div class="progress-spinner"></div>
            <h4>🔍 正在抽取内容...</h4>
            <p class="progress-text">{{ extractionStatus }}</p>
          </div>
          
          <!-- 分析进度 -->
          <div v-if="analyzing" class="analysis-progress">
            <div class="analysis-spinner"></div>
            <h4>🔍 正在分析论文...</h4>
            <p class="analysis-text">{{ analysisStatus }}</p>
          </div>
          
          <!-- 分析结果 -->
          <div v-if="analysisResult" class="analysis-result" :class="analysisResult.success ? 'success' : 'error'">
            <div class="result-icon">{{ analysisResult.success ? '🎉' : '❌' }}</div>
            <h4>{{ analysisResult.success ? '分析完成！' : '分析失败' }}</h4>
            <p>{{ analysisResult.message }}</p>
            <div v-if="analysisResult.success && analysisResult.analysisResult" class="result-details">
              <p><strong>处理耗时：</strong>{{ analysisResult.analysisResult.total_time.toFixed(2) }}秒</p>
              <p><strong>生成对象：</strong>{{ analysisResult.analysisResult.file_check_results.generated_count }}/{{ analysisResult.analysisResult.file_check_results.total_count }}</p>
              <div v-if="analysisResult.analysisResult.generated_files.length > 0" class="generated-files">
                <h5>生成的对象：</h5>
                <ul>
                  <li v-for="file in analysisResult.analysisResult.generated_files" :key="file.filename">
                    {{ file.filename }} ({{ (file.size / 1024).toFixed(1) }}KB)
                  </li>
                </ul>
              </div>
              
              <!-- 跳转到可视化页面的按钮 -->
              <div class="visualization-button">
                <button @click="goToVisualization" class="btn btn-success">
                  <span class="btn-icon">📊</span>
                  查看可视化结果
                </button>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="action-buttons">
            <button 
              v-if="!uploading && !uploadResult?.success && !analyzing && !analysisResult" 
              @click="triggerFileInput" 
              class="btn btn-primary">
              <span class="btn-icon">📄</span>
              选择PDF文件
            </button>
            <button 
              v-if="analysisData || analysisResult" 
              @click="resetAll" 
              class="btn btn-secondary">
              <span class="btn-icon">🔄</span>
              重新开始
            </button>
          </div>
          
          
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { analyzePaper } from '../api/paperAnalysis.js'

export default {
  name: 'FolderUpload',
  data() {
    return {
      isDragOver: false,
      uploading: false,
      uploadProgress: 0,
      uploadStatus: '',
      uploadResult: null,
      selectedFiles: [],
      analyzing: false,
      analysisStatus: '',
      analysisResult: null,
      analysisData: null, // 保存分析结果数据
      parsingProgress: false,
      parsingStatus: '',
      extractionProgress: false,
      extractionStatus: '',
      progressTimer: null,
      features: [
        {
          id: 1,
          icon: '📝',
          title: '摘要语步分析',
          description: '智能提取论文摘要的四个标准语步结构'
        },
        {
          id: 2,
          icon: '🏊',
          title: '内容分区划分',
          description: '将论文章节自动映射到四个标准内容分区'
        },
        {
          id: 3,
          icon: '📊',
          title: '图表映射',
          description: '智能识别论文中的图表并映射到相应内容泳道'
        },
        {
          id: 4,
          icon: '⚡',
          title: '并发处理',
          description: '多进程并行处理，高效分析大规模论文'
        },
        {
          id: 5,
          icon: '🎯',
          title: '智能分析',
          description: '基于大语言模型的跨学科语义理解'
        },
        {
          id: 6,
          icon: '📋',
          title: '结构化输出',
          description: '生成9组标准化的JSON对象，便于后续分析'
        }
      ]
    }
  },
  beforeUnmount() {
    // 组件销毁前清除定时器
    if (this.progressTimer) {
      clearInterval(this.progressTimer)
      this.progressTimer = null
    }
  },
  methods: {
    // 触发文件选择
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    
    // 处理文件选择
    handleFileSelect(event) {
      const files = Array.from(event.target.files)
      if (files.length > 0) {
        // 验证文件类型
        const pdfFile = files.find(file => file.type === 'application/pdf')
        if (!pdfFile) {
          alert('请选择PDF文件')
          return
        }
        this.selectedFiles = [pdfFile] // 只处理第一个PDF文件
        this.startUpload([pdfFile])
      }
    },
    
    // 处理拖拽
    handleDrop(event) {
      event.preventDefault()
      this.isDragOver = false
      
      const files = Array.from(event.dataTransfer.files)
      if (files.length > 0) {
        // 验证文件类型
        const pdfFile = files.find(file => file.type === 'application/pdf')
        if (!pdfFile) {
          alert('请拖拽PDF文件')
          return
        }
        this.selectedFiles = [pdfFile] // 只处理第一个PDF文件
        this.startUpload([pdfFile])
      }
    },
    
    // 开始上传和分析
    async startUpload(files) {
      this.uploading = true
      this.uploadProgress = 0
      this.uploadStatus = '准备分析PDF文件...'
      this.uploadResult = null
      
      // 启动动态进度显示
      this.startDynamicProgress()
      
      try {
        const pdfFile = files[0] // 只处理第一个PDF文件
        
        // 直接调用论文分析API
        const result = await analyzePaper(pdfFile, (progress, status) => {
          this.uploadProgress = progress
          this.uploadStatus = status
        })
        
        if (result.success) {
          // 保存分析结果
          this.analysisData = result.data
          this.uploadResult = {
            success: true,
            message: '分析完成！'
          }
          
          // 显示分析结果
          this.analysisResult = {
            success: true,
            message: '论文分析完成！',
            analysisResult: {
              total_time: result.duration,
              metadata: result.metadata,
              generated_files: [
                { filename: 'paper_vis_upload_result.json', size: JSON.stringify(result.data).length }
              ],
              file_check_results: {
                generated_count: 1,
                total_count: 1
              }
            }
          }
          
          // 自动跳转到可视化页面
          setTimeout(() => {
            this.goToVisualization()
          }, 1000)
          
        } else {
          this.uploadResult = {
            success: false,
            message: result.error || '分析失败'
          }
        }
        
      } catch (error) {
        console.error('分析错误:', error)
        this.uploadResult = {
          success: false,
          message: `分析失败: ${error.message}`
        }
      } finally {
        this.uploading = false
        this.uploadProgress = 100
        // 清除动态进度定时器
        if (this.progressTimer) {
          clearInterval(this.progressTimer)
          this.progressTimer = null
        }
      }
    },
    
    // 启动动态进度显示
    startDynamicProgress() {
      let startTime = Date.now()
      let currentPhase = 0 // 0: 上传, 1: 解析, 2: 抽取
      
      this.progressTimer = setInterval(() => {
        const elapsed = (Date.now() - startTime) / 1000 // 秒
        
        if (elapsed <= 4) {
          // 0-4秒：PDF正在上传
          if (currentPhase !== 0) {
            currentPhase = 0
            this.uploadStatus = '📤 PDF正在上传...'
            this.uploadProgress = Math.min(20, (elapsed / 4) * 20)
          }
        } else if (elapsed <= 20) {
          // 5-20秒：PDF正在解析
          if (currentPhase !== 1) {
            currentPhase = 1
            this.uploadStatus = '📄 PDF正在解析...'
          }
          this.uploadProgress = Math.min(60, 20 + ((elapsed - 4) / 16) * 40)
        } else {
          // 21秒+：正在抽取论文脉络
          if (currentPhase !== 2) {
            currentPhase = 2
            this.uploadStatus = '🔍 正在抽取论文脉络...'
          }
          this.uploadProgress = Math.min(90, 60 + ((elapsed - 20) / 10) * 30)
        }
      }, 500) // 每500ms更新一次
    },
    
    
    // 跳转到可视化页面
    goToVisualization() {
      if (this.analysisData) {
        try {
          // 将分析数据编码后通过路由传递
          // 使用 encodeURIComponent 处理包含非 Latin1 字符的字符串
          const jsonString = JSON.stringify(this.analysisData)
          const encodedData = encodeURIComponent(jsonString)
          this.$router.push({
            path: '/visualization',
            query: { data: encodedData }
          })
        } catch (error) {
          console.error('编码数据时出错:', error)
          alert('数据编码失败，请重试')
        }
      } else {
        alert('没有可用的分析数据')
      }
    },
    
    // 重置所有状态
    resetAll() {
      this.uploadResult = null
      this.analysisResult = null
      this.analysisData = null
      this.selectedFiles = []
      this.uploadProgress = 0
      this.uploadStatus = ''
      this.analysisStatus = ''
      this.analyzing = false
      this.uploading = false
      
      // 清除动态进度定时器
      if (this.progressTimer) {
        clearInterval(this.progressTimer)
        this.progressTimer = null
      }
    }
  }
}
</script>

<style scoped>
/* 单屏布局样式 */
.single-page {
  min-height: 100vh;
  width: 100vw;
  background: #0a0a0a;
  color: #ffffff;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  overflow-x: hidden;
  overflow-y: auto;
  position: relative;
}

.page-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  z-index: 1;
}

.background-particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.2) 0%, transparent 50%);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.main-container {
  position: relative;
  z-index: 2;
  min-height: 100vh;
  display: flex;
  padding: 20px;
  gap: 30px;
}

/* 左侧面板 */
.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  margin-right: 15px;
}

.title-section {
  margin-bottom: 30px;
}

.system-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  padding: 6px 16px;
  margin-bottom: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.badge-icon {
  font-size: 1rem;
}

.main-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 15px;
  line-height: 1.1;
}

.gradient-text {
  background: linear-gradient(45deg, #f093fb, #f5576c);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.main-description {
  font-size: 1rem;
  opacity: 0.9;
  line-height: 1.5;
}

.features-section {
  flex: 1;
  margin-bottom: 20px;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 15px;
  background: linear-gradient(45deg, #1d42e5, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px;
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-2px);
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.1);
}

.feature-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.feature-content {
  flex: 1;
}

.feature-title {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 4px;
  color: #ffffff;
}

.feature-desc {
  font-size: 0.75rem;
  opacity: 0.8;
  line-height: 1.3;
  margin: 0;
}

.stats-section {
  display: flex;
  justify-content: space-between;
  gap: 15px;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-number {
  font-size: 1.8rem;
  font-weight: 800;
  background: linear-gradient(45deg, #f093fb, #f5576c);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.7rem;
  opacity: 0.8;
  font-weight: 500;
}

/* 右侧面板 */
.right-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  margin-left: 15px;
}

.upload-container {
  width: 100%;
}

.upload-header {
  text-align: center;
  margin-bottom: 30px;
}

.upload-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 10px;
  background: linear-gradient(45deg, #3355e9, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.upload-subtitle {
  font-size: 0.9rem;
  opacity: 0.8;
}

.upload-area {
  border: 3px dashed rgba(255, 255, 255, 0.3);
  border-radius: 15px;
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
}

.upload-area:hover,
.upload-area.dragover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  transform: scale(1.02);
}

.upload-content {
  pointer-events: none;
}

.upload-icon {
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.upload-content h3 {
  color: #ffffff;
  margin-bottom: 10px;
  font-size: 1.2rem;
  font-weight: 600;
}

.upload-content p {
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 15px;
  font-size: 0.9rem;
}

.file-requirements {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 15px;
  margin-top: 15px;
  text-align: left;
}

.requirement-title {
  font-size: 0.8rem;
  font-weight: 600;
  margin-bottom: 8px;
  color: #ffffff;
}

.requirement-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.requirement-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
}

.file-icon {
  font-size: 0.9rem;
}

.upload-progress {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.progress-header h4 {
  color: #ffffff;
  margin: 0;
  font-size: 1rem;
}

.progress-text {
  font-weight: 700;
  font-size: 1rem;
  background: linear-gradient(45deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.progress-detail {
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-size: 0.8rem;
}

.upload-result {
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 15px;
  text-align: center;
  backdrop-filter: blur(10px);
}

.upload-result.success {
  background: rgba(16, 185, 129, 0.1);
  border: 2px solid rgba(16, 185, 129, 0.3);
}

.upload-result.error {
  background: rgba(239, 68, 68, 0.1);
  border: 2px solid rgba(239, 68, 68, 0.3);
}

.result-icon {
  font-size: 1.5rem;
  margin-bottom: 8px;
}

.upload-result h4 {
  margin: 0 0 10px 0;
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 600;
}

.upload-result p {
  margin: 0 0 15px 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

.result-details {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 8px;
  margin-top: 10px;
  text-align: left;
}

.result-details p {
  margin: 4px 0;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.9);
}

/* 简化的上传结果提示 */
.upload-result-simple {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 16px;
  margin-bottom: 15px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
  animation: fadeInOut 1s ease-in-out;
}

.upload-result-simple.success {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #10b981;
}

.upload-result-simple.error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.upload-result-simple .result-icon {
  font-size: 1rem;
  margin: 0;
}

@keyframes fadeInOut {
  0% { opacity: 0; transform: translateY(-10px); }
  20% { opacity: 1; transform: translateY(0); }
  80% { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-10px); }
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  position: relative;
  overflow: hidden;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.btn:hover::before {
  left: 100%;
}

.btn-icon {
  font-size: 1rem;
}

.btn-primary {
  background: linear-gradient(45deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-1px);
}

.btn-success {
  background: linear-gradient(45deg, #10b981, #059669);
  color: white;
  box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
}

.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .main-container {
    gap: 20px;
    padding: 15px;
  }
  
  .left-panel,
  .right-panel {
    padding: 30px;
  }
  
  .main-title {
    font-size: 2.2rem;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}

@media (max-width: 1200px) {
  .main-container {
    flex-direction: column;
    gap: 20px;
    padding: 15px;
  }
  
  .left-panel,
  .right-panel {
    margin: 0;
    padding: 25px;
  }
  
  .features-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .stats-section {
    justify-content: center;
    gap: 30px;
  }
  
  .upload-container {
    max-width: 600px;
    margin: 0 auto;
  }
}

@media (max-width: 992px) {
  .main-title {
    font-size: 2rem;
  }
  
  .upload-title {
    font-size: 1.6rem;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stats-section {
    flex-direction: column;
    gap: 15px;
  }
}

@media (max-width: 768px) {
  .main-container {
    padding: 10px;
  }
  
  .left-panel,
  .right-panel {
    padding: 20px;
  }
  
  .main-title {
    font-size: 1.8rem;
  }
  
  .upload-title {
    font-size: 1.4rem;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .feature-item {
    padding: 10px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 10px;
  }
  
  .upload-area {
    padding: 20px 15px;
  }
  
  .upload-result {
    padding: 12px;
  }
  
  .result-details {
    padding: 6px;
  }
}

@media (max-width: 576px) {
  .main-container {
    padding: 8px;
  }
  
  .left-panel,
  .right-panel {
    padding: 15px;
  }
  
  .main-title {
    font-size: 1.5rem;
  }
  
  .upload-title {
    font-size: 1.2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .feature-item {
    padding: 8px;
  }
  
  .upload-area {
    padding: 15px 10px;
  }
  
  .upload-icon {
    font-size: 2rem;
  }
  
  .upload-content h3 {
    font-size: 1rem;
  }
  
  .btn {
    padding: 10px 16px;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .main-container {
    padding: 5px;
  }
  
  .left-panel,
  .right-panel {
    padding: 12px;
  }
  
  .main-title {
    font-size: 1.3rem;
  }
  
  .upload-title {
    font-size: 1.1rem;
  }
  
  .feature-item {
    padding: 6px;
  }
  
  .upload-area {
    padding: 12px 8px;
  }
  
  .upload-icon {
    font-size: 1.8rem;
  }
  
  .btn {
    padding: 8px 12px;
    font-size: 0.8rem;
  }
  
  .scroll-hint {
    padding: 8px;
  }
  
  .scroll-hint p {
    font-size: 0.75rem;
  }
}

/* 分析进度样式 */
/* PDF解析进度样式 */
.parsing-progress {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(52, 152, 219, 0.3);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
}

.parsing-progress h4 {
  color: #3498db;
  margin-bottom: 10px;
  font-size: 1.1rem;
}

/* 内容抽取进度样式 */
.extraction-progress {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(155, 89, 182, 0.3);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
}

.extraction-progress h4 {
  color: #9b59b6;
  margin-bottom: 10px;
  font-size: 1.1rem;
}

/* 通用进度样式 */
.parsing-progress .progress-spinner,
.extraction-progress .progress-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(102, 126, 234, 0.3);
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

.progress-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.analysis-progress {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 15px;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
}

.analysis-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(102, 126, 234, 0.3);
  border-top: 3px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.analysis-progress h4 {
  color: #667eea;
  margin-bottom: 10px;
  font-size: 1.1rem;
}

.analysis-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

/* 分析结果样式 */
.analysis-result {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.analysis-result.success {
  border-color: rgba(76, 175, 80, 0.3);
  background: rgba(76, 175, 80, 0.05);
}

.analysis-result.error {
  border-color: rgba(244, 67, 54, 0.3);
  background: rgba(244, 67, 54, 0.05);
}

.generated-files {
  margin-top: 15px;
}

.generated-files h5 {
  color: #ffffff;
  font-size: 0.9rem;
  margin-bottom: 8px;
}

.generated-files ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.generated-files li {
  background: rgba(255, 255, 255, 0.05);
  padding: 8px 12px;
  margin-bottom: 5px;
  border-radius: 8px;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.9);
}

.visualization-button {
  margin-top: 15px;
  text-align: center;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.btn:disabled:hover {
  transform: none !important;
  box-shadow: inherit !important;
}

/* 滚动提示样式 */
.scroll-hint {
  text-align: center;
  margin-top: 15px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.scroll-hint p {
  margin: 0;
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.7);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}
</style>
