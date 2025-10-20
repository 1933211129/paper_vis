<template>
  <div class="about">
    <h1>关于项目</h1>
    <div class="content">
      <h2>技术栈</h2>
      <div class="tech-stack">
        <div class="tech-item">
          <h3>前端</h3>
          <ul>
            <li>Vue 3</li>
            <li>Vue Router</li>
            <li>Vuex</li>
            <li>Axios</li>
          </ul>
        </div>
        <div class="tech-item">
          <h3>后端</h3>
          <ul>
            <li>Django 4.2</li>
            <li>Python 3.11</li>
            <li>SQLite</li>
          </ul>
        </div>
        <div class="tech-item">
          <h3>容器化</h3>
          <ul>
            <li>Docker</li>
            <li>Docker Compose</li>
            <li>Node.js 18 Alpine</li>
            <li>Python 3.11 Slim</li>
          </ul>
        </div>
      </div>
      
      <h2>项目特性</h2>
      <ul class="features">
        <li>前后端分离架构</li>
        <li>Docker容器化开发环境</li>
        <li>热重载开发体验</li>
        <li>代码实时同步</li>
        <li>跨平台兼容（支持M4芯片）</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AboutPage'
}
</script>

<style scoped>
.about {
  text-align: center;
}

.content {
  max-width: 800px;
  margin: 0 auto;
  text-align: left;
}

.tech-stack {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.tech-item {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.tech-item h3 {
  color: #42b883;
  margin-top: 0;
}

.tech-item ul {
  list-style: none;
  padding: 0;
}

.tech-item li {
  padding: 0.25rem 0;
  border-bottom: 1px solid #e9ecef;
}

.tech-item li:last-child {
  border-bottom: none;
}

.features {
  background: #e3f2fd;
  padding: 1.5rem;
  border-radius: 8px;
  list-style: none;
}

.features li {
  padding: 0.5rem 0;
  position: relative;
  padding-left: 1.5rem;
}

.features li:before {
  content: "✓";
  color: #42b883;
  font-weight: bold;
  position: absolute;
  left: 0;
}
</style>
