#!/bin/bash

###############################################################################
# Agentic Chat 开发环境一键启动脚本
#
# 功能：
# - 同时启动后端（FastAPI）和前端（React + Vite）
# - 自动检测端口占用
# - 彩色输出日志
# - 支持 Ctrl+C 优雅退出
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
BACKEND_PORT=8000
FRONTEND_PORT=3000
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"

# PID 文件
PID_FILE=".dev-pids"

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}正在停止所有服务...${NC}"
    
    if [ -f "$PID_FILE" ]; then
        while read pid; do
            if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
                echo -e "${CYAN}停止进程: $pid${NC}"
                kill -TERM "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    
    echo -e "${GREEN}✓ 所有服务已停止${NC}"
    exit 0
}

# 注册清理函数
trap cleanup SIGINT SIGTERM EXIT

# 检查端口是否被占用
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${RED}✗ 端口 $port 已被占用${NC}"
        echo -e "${YELLOW}  请先停止占用该端口的进程，或修改配置使用其他端口${NC}"
        lsof -i :$port | grep LISTEN
        return 1
    fi
    return 0
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}✗ 未找到 $1 命令${NC}"
        echo -e "${YELLOW}  请先安装 $1${NC}"
        return 1
    fi
    return 0
}

# 打印 banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║        🤖  Agentic Chat - 开发环境启动器  🚀             ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查环境
check_environment() {
    echo -e "${BLUE}检查运行环境...${NC}\n"
    
    # 检查 Python
    if ! check_command python3; then
        exit 1
    fi
    echo -e "${GREEN}✓ Python 已安装${NC}"
    
    # 检查 Node.js
    if ! check_command node; then
        exit 1
    fi
    echo -e "${GREEN}✓ Node.js 已安装${NC}"
    
    # 检查 npm
    if ! check_command npm; then
        exit 1
    fi
    echo -e "${GREEN}✓ npm 已安装${NC}"
    
    # 检查端口
    echo ""
    if ! check_port $BACKEND_PORT || ! check_port $FRONTEND_PORT; then
        exit 1
    fi
    echo -e "${GREEN}✓ 端口检查通过${NC}\n"
}

# 检查依赖
check_dependencies() {
    echo -e "${BLUE}检查项目依赖...${NC}\n"
    
    # 检查后端依赖
    if [ ! -d "backend/.venv" ]; then
        echo -e "${YELLOW}未找到虚拟环境，正在创建...${NC}"
        cd backend
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        cd ..
        echo -e "${GREEN}✓ 后端依赖已安装${NC}"
    else
        echo -e "${GREEN}✓ 后端虚拟环境已存在${NC}"
    fi
    
    # 检查前端依赖
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        echo -e "${YELLOW}未找到前端依赖，正在安装...${NC}"
        cd $FRONTEND_DIR
        npm install
        cd ..
        echo -e "${GREEN}✓ 前端依赖已安装${NC}"
    else
        echo -e "${GREEN}✓ 前端依赖已存在${NC}"
    fi
    
    echo ""
}

# 启动后端
start_backend() {
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}启动后端服务 (FastAPI)...${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    
    # 启动后端
    cd $BACKEND_DIR
    
    # 检查虚拟环境是否存在
    if [ ! -f ".venv/bin/python" ]; then
        echo -e "${RED}✗ 未找到 backend/.venv 虚拟环境${NC}"
        echo -e "${YELLOW}  请先运行: cd backend && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt${NC}"
        exit 1
    fi
    
    # 使用 backend/.venv/bin/python 明确指定 Python 解释器
    # 设置 PYTHONPATH 并启动后端（后台运行）
    PYTHONPATH=$PWD .venv/bin/python -m app.main > logs/dev-backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    echo $BACKEND_PID >> $PID_FILE
    
    echo -e "${GREEN}✓ 后端服务已启动${NC}"
    echo -e "${CYAN}  PID: $BACKEND_PID${NC}"
    echo -e "${CYAN}  URL: http://localhost:$BACKEND_PORT${NC}"
    echo -e "${CYAN}  Docs: http://localhost:$BACKEND_PORT/docs${NC}"
    echo -e "${CYAN}  日志: logs/dev-backend.log${NC}\n"
    
    # 等待后端启动
    echo -e "${YELLOW}等待后端服务启动...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:$BACKEND_PORT/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 后端服务已就绪${NC}\n"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    echo -e "\n${RED}✗ 后端服务启动超时${NC}"
    return 1
}

# 启动前端
start_frontend() {
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}启动前端服务 (React + Vite)...${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    
    cd $FRONTEND_DIR
    
    # 启动前端（后台运行）
    npm run dev > ../logs/dev-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID >> ../$PID_FILE
    
    cd ..
    
    echo -e "${GREEN}✓ 前端服务已启动${NC}"
    echo -e "${CYAN}  PID: $FRONTEND_PID${NC}"
    echo -e "${CYAN}  URL: http://localhost:$FRONTEND_PORT${NC}"
    echo -e "${CYAN}  日志: logs/dev-frontend.log${NC}\n"
    
    # 等待前端启动
    echo -e "${YELLOW}等待前端服务启动...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 前端服务已就绪${NC}\n"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    echo -e "\n${YELLOW}⚠ 前端服务可能需要更长时间启动${NC}\n"
}

# 显示日志
show_logs() {
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${PURPLE}实时日志 (Ctrl+C 停止所有服务)${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    
    echo -e "${GREEN}✅ 所有服务已启动！${NC}\n"
    echo -e "${CYAN}📝 访问地址：${NC}"
    echo -e "${CYAN}   前端: http://localhost:$FRONTEND_PORT${NC}"
    echo -e "${CYAN}   后端: http://localhost:$BACKEND_PORT${NC}"
    echo -e "${CYAN}   API文档: http://localhost:$BACKEND_PORT/docs${NC}\n"
    
    echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}\n"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
    
    # 实时显示日志
    tail -f logs/dev-backend.log logs/dev-frontend.log 2>/dev/null
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p logs
    
    # 清理旧的 PID 文件
    rm -f $PID_FILE
    
    # 打印 banner
    print_banner
    
    # 检查环境
    check_environment
    
    # 检查依赖
    check_dependencies
    
    # 启动服务
    start_backend
    start_frontend
    
    # 显示日志
    show_logs
}

# 运行主函数
main

