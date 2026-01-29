/**
 * 前端配置文件 - API 端点配置
 * 
 * 使用说明:
 * 1. 本地开发: 改为 http://localhost:5000
 * 2. 生产环境: 改为后端服务器的实际地址
 */

// API 配置
const API_CONFIG = {
  // 选项 1: 本地开发 (后端运行在本地)
  // baseURL: 'http://localhost:5000/api',
  
  // 选项 2: 远程后端服务器
  // 需要将后端部署到具有 CORS 支持的服务器
  baseURL: 'https://arxiv-tracker-backend.herokuapp.com/api',
  
  // 超时时间 (毫秒)
  timeout: 30000,
};

// 导出配置
if (typeof module !== 'undefined' && module.exports) {
  module.exports = API_CONFIG;
}
