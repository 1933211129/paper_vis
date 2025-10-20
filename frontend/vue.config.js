const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    allowedHosts: 'all',
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: 'http://10.3.35.21:8004',
        changeOrigin: true,
        secure: false,
        pathRewrite: {
          '^/api': ''  // 将 /api 重写为空，直接转发到后端
        }
      }
    }
  }
})
