import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // 定义环境变量（避免 .env.local 权限问题）
  define: {
    'import.meta.env.VITE_API_BASE_URL': JSON.stringify('http://localhost:8000'),
    'import.meta.env.VITE_API_VERSION': JSON.stringify('v1'),
    'import.meta.env.VITE_WS_URL': JSON.stringify('ws://localhost:8000/ws'),
  },
  
  // 路径别名
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  
  // 开发服务器配置
  server: {
    port: 3000,
    host: 'localhost',  // 改为 localhost 避免网络接口问题
    strictPort: false,  // 如果端口被占用，自动使用下一个
    
    // 代理配置（开发环境）
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
  
  // 构建配置
  build: {
    outDir: 'dist',
    sourcemap: false,
    
    // 分包策略
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['antd', '@ant-design/icons'],
        },
      },
    },
  },
  
  // 环境变量前缀
  envPrefix: 'VITE_',
});

