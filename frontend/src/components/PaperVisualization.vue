<template>
  <div class="horizontal-paper-visualization">
    <!-- 顶部导航和标题区域 -->
    <header class="paper-header">
      <div class="header-content">
        <div class="paper-title-section">
          <h1 class="paper-title">{{ metadata?.title || 'Paper Title' }}</h1>
          <div class="authors-section">
            <span class="authors-label">Authors:</span>
            
            <div class="authors-list">
              <span v-for="(author, index) in (metadata?.authors || [])" :key="index" class="author-tag">
                {{ author }}
              </span>
      </div>
          </div>
        </div>
        <div class="header-actions">
          <button class="action-btn upload-btn" @click="goToUpload">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14,2 14,8 20,8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10,9 9,9 8,9"/>
            </svg>
            上传新文件
          </button>
        </div>
      </div>
    </header>

    <!-- 摘要概览区域 -->
    <section v-if="abstractData && Object.keys(abstractData).length > 0" class="abstract-overview">
      <div class="overview-container">
        <h2 class="overview-title">Research Overview</h2>
        <div class="abstract-list">
          <div v-for="(content, key) in (abstractData || {})" :key="key" class="overview-item" :class="`overview-${key.toLowerCase().replace(/[^a-z]/g, '')}`">
            <div class="overview-item-header">
              <h3 class="overview-item-title">{{ key }}</h3>
              <div class="overview-indicator"></div>
            </div>
            <p class="overview-item-text">{{ content }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 五个垂直并列的泳道 -->
    <div class="swimlanes-container">
      <!-- Context & Related Work 泳道 -->
      <div class="swimlane">
        <div class="swimlane-header">
          <h2>Context & Related Work</h2>
        </div>
        <div class="swimlane-content">
          <div v-for="(item, key) in getParsedData(contextData)" :key="key" class="content-item">
            <div class="content-card" @mouseenter="showCardPreview(key, item)" @mouseleave="closePreview">
              <h3>{{ key }}</h3>
              <p>{{ truncateText(item, 80) }}</p>
            </div>
          </div>
          <!-- 该泳道的图片 -->
          <div v-if="getFiguresForSection('Context & Related Work').length > 0" class="section-figures">
            <h4 class="figures-title">Context Figures</h4>
            <div class="figures-grid">
              <div 
                v-for="(figure, index) in getFiguresForSection('Context & Related Work')" 
                :key="index" 
                class="figure-card"
                @mouseenter="showFigurePreview(figure)"
                @mouseleave="closeFigurePreview"
              >
                <div class="figure-preview">
                  <img :src="figure.imageSrc" :alt="figure.figure_caption || 'Figure'" class="figure-image" @error="handleImageError" />
                  <div class="figure-overlay">
                    <div class="overlay-content">
                      <svg class="zoom-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
                      </svg>
                      <p class="overlay-text">Click to view</p>
                    </div>
                  </div>
                </div>
                <div class="figure-info">
                  <div class="figure-caption">{{ figure.figure_caption || 'No caption' }}</div>
                  <div v-if="figure.reference_text && figure.reference_text.length > 0" class="figure-references">
                    <span class="ref-label">References:</span>
                    <ul class="ref-list">
                      <li v-for="(ref, idx) in (figure.reference_text || [])" :key="idx" class="ref-item">{{ ref }}</li>
            </ul>
          </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Methodology & Setup 泳道 -->
      <div class="swimlane">
        <div class="swimlane-header">
          <h2>Methodology & Setup</h2>
        </div>
        <div class="swimlane-content">
          <div v-for="(item, key) in getParsedData(methodologyData)" :key="key" class="content-item">
            <div class="content-card" @mouseenter="showCardPreview(key, item)" @mouseleave="closePreview">
              <h3>{{ key }}</h3>
              <p>{{ truncateText(item, 80) }}</p>
            </div>
          </div>
          <!-- 该泳道的图片 -->
          <div v-if="getFiguresForSection('Methodology & Setup').length > 0" class="section-figures">
            <h4 class="figures-title">Methodology Figures</h4>
            <div class="figures-grid">
              <div 
                v-for="(figure, index) in getFiguresForSection('Methodology & Setup')" 
                :key="index" 
                class="figure-card"
                @mouseenter="showFigurePreview(figure)"
                @mouseleave="closeFigurePreview"
              >
                <div class="figure-preview">
                  <img :src="figure.imageSrc" :alt="figure.figure_caption || 'Figure'" class="figure-image" @error="handleImageError" />
                  <div class="figure-overlay">
                    <div class="overlay-content">
                      <svg class="zoom-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
                      </svg>
                      <p class="overlay-text">Click to view</p>
                    </div>
                  </div>
                </div>
                <div class="figure-info">
                  <div class="figure-caption">{{ figure.figure_caption || 'No caption' }}</div>
                  <div v-if="figure.reference_text && figure.reference_text.length > 0" class="figure-references">
                    <span class="ref-label">References:</span>
                    <ul class="ref-list">
                      <li v-for="(ref, idx) in (figure.reference_text || [])" :key="idx" class="ref-item">{{ ref }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Results & Analysis 泳道 -->
      <div class="swimlane">
        <div class="swimlane-header">
          <h2>Results & Analysis</h2>
        </div>
        <div class="swimlane-content">
          <div v-for="(item, key) in getParsedData(resultsData)" :key="key" class="content-item">
            <div class="content-card" @mouseenter="showCardPreview(key, item)" @mouseleave="closePreview">
              <h3>{{ key }}</h3>
              <p>{{ truncateText(item, 80) }}</p>
            </div>
          </div>
          <!-- 该泳道的图片 -->
          <div v-if="getFiguresForSection('Results & Analysis').length > 0" class="section-figures">
            <h4 class="figures-title">Results Figures</h4>
            <div class="figures-grid">
              <div 
                v-for="(figure, index) in getFiguresForSection('Results & Analysis')" 
                :key="index" 
                class="figure-card"
                @mouseenter="showFigurePreview(figure)"
                @mouseleave="closeFigurePreview"
              >
                <div class="figure-preview">
                  <img :src="figure.imageSrc" :alt="figure.figure_caption || 'Figure'" class="figure-image" @error="handleImageError" />
                  <div class="figure-overlay">
                    <div class="overlay-content">
                      <svg class="zoom-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
                      </svg>
                      <p class="overlay-text">Click to view</p>
                    </div>
                  </div>
                </div>
                <div class="figure-info">
                  <div class="figure-caption">{{ figure.figure_caption || 'No caption' }}</div>
                  <div v-if="figure.reference_text && figure.reference_text.length > 0" class="figure-references">
                    <span class="ref-label">References:</span>
                    <ul class="ref-list">
                      <li v-for="(ref, idx) in (figure.reference_text || [])" :key="idx" class="ref-item">{{ ref }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Conclusion 泳道 -->
      <div class="swimlane">
        <div class="swimlane-header">
          <h2>Conclusion</h2>
        </div>
        <div class="swimlane-content">
          <div v-if="conclusionItems.length > 0">
            <div v-for="(item, index) in conclusionItems" :key="index" class="content-item">
              <div class="content-card" @mouseenter="showCardPreview(item.name, item.content)" @mouseleave="closePreview">
                <h3>{{ item.name }}</h3>
                <p>{{ truncateText(item.content, 80) }}</p>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">📝</div>
            <p>No conclusion data available</p>
          </div>
          <!-- 该泳道的图片 -->
          <div v-if="getFiguresForSection('Conclusion').length > 0" class="section-figures">
            <h4 class="figures-title">Conclusion Figures</h4>
            <div class="figures-grid">
              <div 
                v-for="(figure, index) in getFiguresForSection('Conclusion')" 
                :key="index" 
                class="figure-card"
                @mouseenter="showFigurePreview(figure)"
                @mouseleave="closeFigurePreview"
              >
                <div class="figure-preview">
                  <img :src="figure.imageSrc" :alt="figure.figure_caption || 'Figure'" class="figure-image" @error="handleImageError" />
                  <div class="figure-overlay">
                    <div class="overlay-content">
                      <svg class="zoom-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"></path>
                      </svg>
                      <p class="overlay-text">Click to view</p>
                    </div>
                  </div>
                </div>
                <div class="figure-info">
                  <div class="figure-caption">{{ figure.figure_caption || 'No caption' }}</div>
                  <div v-if="figure.reference_text && figure.reference_text.length > 0" class="figure-references">
                    <span class="ref-label">References:</span>
                    <ul class="ref-list">
                      <li v-for="(ref, idx) in (figure.reference_text || [])" :key="idx" class="ref-item">{{ ref }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Innovation Opportunities 泳道 -->
      <div class="swimlane">
        <div class="swimlane-header">
          <h2>Innovation Opportunities</h2>
        </div>
        <div class="swimlane-content">
          <div v-if="innovationItems.length > 0">
            <div v-for="(item, index) in innovationItems" :key="index" class="content-item">
              <div class="content-card" @mouseenter="showCardPreview(item.name, item.content)" @mouseleave="closePreview">
                <h3>{{ item.name }}</h3>
                <p>{{ truncateText(item.content, 80) }}</p>
              </div>
            </div>
          </div>
          <div v-else class="empty-state">
            <div class="empty-icon">💡</div>
            <p>No innovation opportunities data available</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片模态框 -->
    <div v-if="selectedFigure" class="figure-modal" @click="closeFigureModal">
      <div class="modal-content" @click.stop>
        <button class="modal-close" @click="closeFigureModal">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
        <div class="modal-image-container">
          <img :src="selectedFigure.imageSrc" :alt="selectedFigure.figure_caption" class="modal-image" />
        </div>
        <div class="modal-caption">
          <h3 class="modal-title">{{ selectedFigure.figure_caption }}</h3>
          <div v-if="selectedFigure.reference_text && selectedFigure.reference_text.length" class="modal-references">
            <h4 class="references-title">Related References:</h4>
            <ul class="references-list">
              <li v-for="(ref, index) in (selectedFigure?.reference_text || [])" :key="index" class="reference-item">
                {{ ref }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p class="loading-text">Loading Research Data...</p>
      </div>
    </div>
    
    <!-- 悬浮预览框 -->
    <div v-if="hoveredCard" class="card-preview-tooltip">
      <div class="preview-content">
        <div class="preview-header">
          <h3>{{ hoveredCard.title }}</h3>
        </div>
        <div class="preview-body">
          <p>{{ hoveredCard.content }}</p>
        </div>
      </div>
    </div>

    <!-- 悬浮图片预览框 -->
    <div v-if="hoveredFigure" class="figure-preview-tooltip">
      <div class="figure-preview-content">
        <div class="figure-preview-image">
          <img :src="hoveredFigure.imageSrc" :alt="hoveredFigure.figure_caption" class="preview-image" />
        </div>
        <div class="figure-preview-info">
          <h3 class="preview-caption">{{ hoveredFigure.figure_caption || 'No caption' }}</h3>
          <div v-if="hoveredFigure.reference_text && hoveredFigure.reference_text.length > 0" class="preview-references">
            <h4 class="references-title">References:</h4>
            <ul class="references-list">
              <li v-for="(ref, index) in hoveredFigure.reference_text" :key="index" class="reference-item">
                {{ ref }}
              </li>
            </ul>
          </div>
        </div>
      </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
  name: 'HorizontalPaperVisualization',
  data() {
      return {
      loading: true,
      metadata: null,
      abstractData: null,
      contextData: null,
      methodologyData: null,
      resultsData: null,
      conclusionData: null,
      innovationData: null,
      figureMap: null,
      selectedFigure: null,
      hoveredCard: null,
      hoveredFigure: null
    }
  },
  async mounted() {
    await this.loadData()
    this.loading = false
  },
  computed: {
    conclusionItems() {
      const data = this.conclusionData
      if (!data) return []
      
      // 新结构：数组中的对象
      if (Array.isArray(data) && data.length > 0) {
        const items = []
        data.forEach(item => {
          if (typeof item === 'object' && item !== null) {
            Object.entries(item).forEach(([key, value]) => {
              items.push({ name: key, content: value })
            })
          }
        })
        return items
      }
      
      // 兼容旧结构：单个对象
      if (!Array.isArray(data) && typeof data === 'object') {
        return Object.entries(data).map(([key, value]) => ({ name: key, content: value }))
      }
      
      return []
    },
    innovationItems() {
      const data = this.innovationData
      if (!data) return []
      
      // 新结构：数组中的对象
      if (Array.isArray(data) && data.length > 0) {
        const items = []
        data.forEach(item => {
          if (typeof item === 'object' && item !== null) {
            Object.entries(item).forEach(([key, value]) => {
              const prettyKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
              items.push({ name: prettyKey, content: value })
            })
          }
        })
        return items
      }
      
      // 兼容旧结构：单个对象
      if (typeof data === 'object') {
        return Object.entries(data).map(([key, value]) => {
          if (typeof value === 'string') {
            const prettyKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
            return { name: prettyKey, content: value }
          }
          if (value && typeof value === 'object') {
            return { name: value.title || key, content: value.description || '' }
          }
          return { name: key, content: '' }
        })
      }
      
      return []
    }
  },
  methods: {
    // 解析JSON数据，处理数组格式
    getParsedData(data) {
      if (!data) return {}
      
      // 新结构：数组中的对象，需要合并所有对象
      if (Array.isArray(data) && data.length > 0) {
        const result = {}
        data.forEach(item => {
          if (typeof item === 'object' && item !== null) {
            Object.assign(result, item)
          }
        })
        return result
      }
      
      // 兼容旧结构：单个对象
      return data
    },
    
    async loadData() {
      try {
        console.log('Loading research data from route parameters...')
        
        // 从路由参数获取数据
        const encodedData = this.$route.query.data
        if (!encodedData) {
          throw new Error('No data found in route parameters')
        }
        
        // 解码数据
        const data = JSON.parse(decodeURIComponent(encodedData))
        console.log('Raw data loaded:', data)
        
        // 提取各个部分的数据
        this.metadata = data.metadata || null
        this.abstractData = data.abstract || null
        
        // 处理lanes数据 - 适配新的数据结构
        const lanes = data.lanes || {}
        this.contextData = lanes['Context & Related Work'] || null
        this.methodologyData = lanes['Methodology & Setup'] || null
        this.resultsData = lanes['Results & Analysis'] || null
        this.conclusionData = lanes['Conclusion'] || null
        this.innovationData = lanes['Innovation Discovery'] || null
        
        // 处理图片数据 - 包含base64编码
        this.figureMap = data.figure_map || null
        
        console.log('Data loaded successfully')
        console.log('Metadata:', this.metadata)
        console.log('Abstract:', this.abstractData)
        console.log('Figure map:', this.figureMap)
        
      } catch (error) {
        console.error('Failed to load data:', error)
        alert('Failed to load research data: ' + error.message)
      }
    },
    
    
    getFiguresForSection(sectionName) {
      if (!this.figureMap || !this.figureMap[sectionName] || !Array.isArray(this.figureMap[sectionName])) return []
      
      return this.figureMap[sectionName].map(fig => ({
        ...fig,
        imageSrc: this.getImageSrc(fig)
      }))
    },
    
    // 处理base64图片或fallback到默认图片
    getImageSrc(figure) {
      if (figure.figure_base64) {
        // 如果是base64编码的图片，直接使用
        return `data:image/jpeg;base64,${figure.figure_base64}`
      }
      // 如果没有base64，尝试使用figure_id作为文件名
      return `/data/images/${figure.figure_id || 'default'}.jpg`
    },
    
    // 获取所有图片数据
    getAllFigures() {
      if (!this.figureMap || typeof this.figureMap !== 'object') return []
      
      const allFigures = []
      Object.keys(this.figureMap).forEach(section => {
        if (Array.isArray(this.figureMap[section])) {
          this.figureMap[section].forEach(fig => {
            if (fig && typeof fig === 'object') {
              allFigures.push({
                ...fig,
                imageSrc: this.getImageSrc(fig)
              })
            }
          })
        }
      })
      
      return allFigures
    },
    
    openFigureModal(figure) {
      this.selectedFigure = figure
    },
    
    closeFigureModal() {
      this.selectedFigure = null
    },
    
    showFigurePreview(figure) {
      this.hoveredFigure = figure
      // 确保图片能完整显示在预览框内
      this.$nextTick(() => {
        this.adjustPreviewImageSize()
      })
    },
    
    closeFigurePreview() {
      this.hoveredFigure = null
    },
    
    adjustPreviewImageSize() {
      const previewImage = document.querySelector('.preview-image')
      if (!previewImage) return
      
      const container = document.querySelector('.figure-preview-image')
      if (!container) return
      
      const containerWidth = container.clientWidth
      const containerHeight = container.clientHeight
      
      // 获取图片的原始尺寸
      const img = new Image()
      img.onload = () => {
        const imgWidth = img.width
        const imgHeight = img.height
        
        // 计算缩放比例，确保图片完整显示在容器内
        const scaleX = containerWidth / imgWidth
        const scaleY = containerHeight / imgHeight
        const scale = Math.min(scaleX, scaleY, 1) // 不放大，只缩小
        
        // 应用缩放
        previewImage.style.width = `${imgWidth * scale}px`
        previewImage.style.height = `${imgHeight * scale}px`
        previewImage.style.maxWidth = '100%'
        previewImage.style.maxHeight = '100%'
      }
      img.src = previewImage.src
    },
    showCardPreview(title, content) {
      this.hoveredCard = { title, content }
    },
    closePreview() {
      this.hoveredCard = null
    },
    
    handleImageError(event) {
      console.warn('Image failed to load:', event.target.src)
      event.target.src = '/data/images/default.jpg'
    },
    
    truncateText(text, maxLength) {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    },
    
    // 跳转到上传页面
    goToUpload() {
      this.$router.push('/upload')
    }
  }
}
</script>

<style scoped>
/* 全局样式 */
.horizontal-paper-visualization {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: #2d3748;
  line-height: 1.6;
}

/* 头部样式 */
.paper-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.paper-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 1rem 0;
  line-height: 1.2;
}

.authors-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.authors-label {
  font-weight: 600;
  color: #4a5568;
  font-size: 0.9rem;
}

.authors-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.author-tag {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.upload-btn {
  background: linear-gradient(135deg, #667eea, #764ba2);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.upload-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.icon {
  width: 16px;
  height: 16px;
}

.upload-btn .icon {
  width: 14px;
  height: 14px;
}

/* 摘要概览区域 */
.abstract-overview {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem 0;
}

.overview-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
}

.overview-title {
  font-size: 2rem;
  font-weight: 700;
  color: white;
  margin: 0 0 2rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.abstract-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.overview-item {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-left: 4px solid #667eea;
}

.overview-item:hover {
  transform: translateX(4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-left-color: #764ba2;
}

.overview-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.overview-item-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2d3748;
  margin: 0;
}

.overview-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.overview-item-text {
  color: #4a5568;
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.6;
}

/* 四个垂直并列的泳道容器 */
.swimlanes-container {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 1.5rem;
  padding: 1rem;
  width: 100%;
  max-width: none;
  overflow-x: auto;
}

/* 泳道样式 */
.swimlane {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s ease;
}

.swimlane:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.swimlane-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-height: 4rem;
}

.swimlane-header h2 {
  font-weight: 600;
  margin: 0;
  font-size: clamp(0.6rem, 1.2vw + 0.4rem, 1.1rem);
  line-height: 1.3;
  white-space: normal;
  word-wrap: break-word;
  hyphens: auto;
  text-align: center;
  padding: 0.2rem;
}

.swimlane-content {
  padding: 1rem;
}

/* Content Items */
.content-item {
  margin-bottom: 1rem;
  padding: 0;
  background: transparent;
  border-radius: 0;
  border: none;
  transition: all 0.3s ease;
}

.content-item:hover {
  background: transparent;
  transform: none;
}

.content-item h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.8rem;
}

.content-item p {
  color: #4a5568;
  line-height: 1.6;
  margin: 0;
}

/* Section Figures */
.section-figures {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 2px solid #e2e8f0;
}

.figures-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 1rem;
  text-align: center;
}

/* 图片展示 */
.figures-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.figure-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  width: 80px;
  height: 60px;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.figure-card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
}

.figure-preview {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.figure-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

/* 图片缩略图样式 */
.figure-preview {
  width: 80px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.figure-preview:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.figure-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.5));
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.overlay-content {
  text-align: center;
  color: white;
}

.figure-card:hover .figure-overlay {
  opacity: 1;
}

.figure-card:hover .figure-image {
  transform: scale(1.1);
}

.zoom-icon {
  width: 40px;
  height: 40px;
  color: white;
  margin-bottom: 8px;
}

.overlay-text {
  font-size: 14px;
  font-weight: 500;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.figure-info {
  display: none; /* 缩略图模式下隐藏详细信息 */
}

.figure-caption {
  font-size: 0.9rem;
  color: #4a5568;
  line-height: 1.4;
  margin-bottom: 8px;
}

.figure-references {
  font-size: 0.8rem;
  color: #718096;
}

.ref-label {
  font-weight: 600;
  margin-right: 4px;
  display: block;
  margin-bottom: 0.5rem;
}

.ref-list {
  margin: 0;
  padding-left: 1rem;
}

.ref-item {
  font-size: 0.75rem;
  line-height: 1.4;
  margin-bottom: 0.3rem;
  color: #6b7280;
}

/* 模态框 */
.figure-modal {
  position: fixed;
    top: 0;
    left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.modal-content {
  background: white;
  border-radius: 20px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 40px;
  height: 40px;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
  transition: background 0.3s ease;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.7);
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.modal-image-container {
  max-height: 60vh;
  overflow: hidden;
}

.modal-image {
    width: 100%;
  height: auto;
  object-fit: contain;
}

.modal-caption {
  padding: 2rem;
}

.modal-title {
  font-size: 1.25rem;
    font-weight: 600;
  color: #2d3748;
  margin: 0 0 1rem 0;
}

.references-title {
  font-size: 1rem;
  font-weight: 600;
  color: #4a5568;
  margin: 1rem 0 0.5rem 0;
}

.references-list {
  margin: 0;
  padding-left: 1.5rem;
}

.reference-item {
  color: #6b7280;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
    top: 0;
    left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.loading-spinner {
    text-align: center;
  color: white;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

.loading-text {
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 所有卡片现在都使用统一的content-card样式 */

/* 统一的内容卡片样式 */
.content-card {
  background: white;
  border-radius: 6px;
  padding: 0.8rem;
  border: 1px solid #e5e7eb;
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
  height: 100px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.content-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.content-card h3 {
  color: #374151;
  margin-bottom: 0.4rem;
  font-size: 0.85rem;
    font-weight: 600;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.content-card p {
    color: #6b7280;
  line-height: 1.3;
  margin: 0;
  font-size: 0.8rem;
  flex-grow: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
}

/* Innovation卡片现在也使用统一的content-card样式 */

/* 悬浮图片预览框样式 */
.figure-preview-tooltip {
    position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1500;
  pointer-events: none;
}

.figure-preview-content {
  background: white;
  border-radius: 12px;
  max-width: 50vw;
  max-height: 70vh;
  width: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.figure-preview-image {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  min-height: 100px;
  max-height: 30vh;
  width: 100%;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  object-position: center;
  border-radius: 8px;
  display: block;
  margin: auto;
}

.figure-preview-info {
  padding: 15px;
  flex-shrink: 0;
  border-top: 1px solid #e2e8f0;
    background: #ffffff;
  /* 移除高度限制，让内容完整显示 */
}

.preview-caption {
  color: #2d3748;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 15px 0;
  line-height: 1.4;
  word-wrap: break-word;
  white-space: normal;
}

.preview-references {
  margin-top: 15px;
}

.references-title {
  color: #4a5568;
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.references-list {
  margin: 0;
  padding-left: 20px;
}

.reference-item {
  color: #6b7280;
  font-size: 0.85rem;
  line-height: 1.4;
  margin-bottom: 4px;
  word-wrap: break-word;
  white-space: normal;
}

/* 响应式设计 */
@media (max-height: 600px) {
  .figure-preview-content {
    max-height: 80vh;
  }
  
  .figure-preview-image {
    min-height: 80px;
    max-height: 35vh;
  }
  
  .figure-preview-info {
    padding: 10px;
  }
}

@media (max-width: 768px) {
  .figure-preview-content {
    max-width: 85vw;
    max-height: 60vh;
    margin: 8px;
  }
  
  .figure-preview-image {
    max-height: 25vh;
  }
  
  .figure-preview-info {
    padding: 10px;
  }
}

/* 悬浮预览框样式 */
.card-preview-tooltip {
    position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1500;
    pointer-events: none;
}

.preview-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  max-height: 400px;
  width: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  animation: previewSlideIn 0.3s ease;
  pointer-events: auto;
  position: relative;
  border: 1px solid #e0e0e0;
}

.preview-header {
  background: #f8f9fa;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.preview-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.preview-body {
  padding: 1rem;
  max-height: 300px;
  overflow-y: auto;
}

.preview-body p {
  margin: 0;
  line-height: 1.6;
  color: #555;
}

@keyframes previewSlideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}


.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.preview-body {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
}

.preview-body p {
  margin: 0;
  line-height: 1.6;
  color: #4b5563;
  font-size: 0.95rem;
}

/* 响应式设计 */

/* 简化的响应式设计 - 确保标题在所有屏幕尺寸下都能完整显示 */
@media (max-width: 1200px) {
  .swimlane-header h2 {
    font-size: clamp(0.5rem, 1vw + 0.3rem, 0.9rem);
  }
}

@media (max-width: 992px) {
  .swimlane-header h2 {
    font-size: clamp(0.45rem, 0.9vw + 0.25rem, 0.8rem);
  }
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1.5rem;
    text-align: center;
  }
  
  .paper-title {
    font-size: 1.5rem;
  }
  
  .authors-section {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .overview-container {
    padding: 0 1rem;
  }
  
  .abstract-list {
    gap: 0.75rem;
  }
  
  .swimlanes-container {
    grid-template-columns: 1fr;
    padding: 1rem;
    gap: 1rem;
  }
  
  .swimlane-header {
    padding: 1rem 1.5rem;
  }
  
  .swimlane-header h2 {
    font-size: clamp(0.4rem, 0.8vw + 0.3rem, 0.7rem);
    line-height: 1.4;
  }
  
  .swimlane-content {
    padding: 1.5rem;
  }
}

@media (max-width: 480px) {
  .paper-header {
    padding: 1rem;
  }
  
  .header-content {
    padding: 1rem;
  }
  
  .overview-container {
    padding: 0 0.5rem;
  }
  
  .research-lane {
    padding: 0.5rem;
  }
  
  .flow-header {
    padding: 1rem;
  }
  
  .flow-indicators {
    flex-wrap: wrap;
  }
  
  .indicator {
    font-size: 0.8rem;
    padding: 0.4rem 0.8rem;
  }
  
  .swimlane-header h2 {
    font-size: clamp(0.35rem, 0.7vw + 0.25rem, 0.6rem);
    line-height: 1.4;
  }
}
  </style>