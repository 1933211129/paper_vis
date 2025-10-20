<template>
  <div class="home">
    <h1>📚 学术论文智能分析系统</h1>
    <div class="status-card">
      <h2>后端状态</h2>
      <p>状态: <span :class="statusClass">{{ backendStatus }}</span></p>
      <button @click="checkStatus" class="check-btn">检查状态</button>
    </div>
    
    <div class="action-card">
      <h2>🚀 开始分析</h2>
      <p>上传包含论文文件的文件夹，开始智能分析</p>
      <router-link to="/upload" class="upload-btn">
        📁 上传文件夹
      </router-link>
    </div>
    
    <div class="info-card">
      <h2>📋 项目信息</h2>
      <ul>
        <li>前端: Vue 3 + Vue Router + Vuex</li>
        <li>后端: Django 4.2 + 论文分析模块</li>
        <li>容器化: Docker + Docker Compose</li>
        <li>开发端口: 前端 8022, 后端 8021</li>
        <li>功能: 摘要分析、内容泳道划分、图表映射</li>
      </ul>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'HomePage',
  computed: {
    ...mapState(['backendStatus']),
    statusClass() {
      return {
        'status-ok': this.backendStatus === 'ok',
        'status-error': this.backendStatus === 'error',
        'status-unknown': this.backendStatus === 'unknown'
      }
    }
  },
  methods: {
    ...mapActions(['checkBackendStatus']),
    checkStatus() {
      this.checkBackendStatus()
    }
  },
  mounted() {
    console.log('Home component mounted, checking backend status...')
    this.checkBackendStatus()
  }
}
</script>

<style scoped>
.home {
  text-align: center;
}

.status-card, .action-card, .info-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 2rem;
  margin: 2rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.action-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-card h2, .action-card p {
  color: white;
}

.upload-btn {
  display: inline-block;
  background: white;
  color: #667eea;
  padding: 1rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  font-size: 1.1rem;
  margin-top: 1rem;
  transition: all 0.3s ease;
}

.upload-btn:hover {
  background: #f8f9ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.status-ok {
  color: #28a745;
  font-weight: bold;
}

.status-error {
  color: #dc3545;
  font-weight: bold;
}

.status-unknown {
  color: #6c757d;
  font-weight: bold;
}

.check-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.check-btn:hover {
  background-color: #0056b3;
}

.info-card ul {
  text-align: left;
  max-width: 400px;
  margin: 0 auto;
}

.info-card li {
  margin: 0.5rem 0;
}
</style>
