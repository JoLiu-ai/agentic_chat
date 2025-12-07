#!/bin/bash
###############################################################################
# Agentic Chat 开发环境启动脚本（简化版）
###############################################################################

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   🤖 Agentic Chat - 开发环境启动器 🚀  ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════╝${NC}\n"

# 检查并安装前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}正在安装前端依赖...${NC}"
    cd frontend && npm install && cd ..
    echo -e "${GREEN}✓ 前端依赖已安装${NC}\n"
fi

echo -e "${BLUE}启动服务...${NC}\n"

# 使用 npm 的 concurrently
npm run dev

