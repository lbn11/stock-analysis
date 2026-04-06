#!/bin/bash

###############################################
# CMoney 股价预测系统 - 停止脚本
# 版本: v1.0
###############################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}🛑 停止 CMoney 系统...${NC}"

# 停止后端
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        echo -e "${GREEN}✓ 后端已停止 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  后端进程不存在${NC}"
    fi
    rm -f .backend.pid
else
    echo -e "${YELLOW}⚠️  未找到后端 PID 文件${NC}"
fi

# 停止前端
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        echo -e "${GREEN}✓ 前端已停止 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${YELLOW}⚠️  前端进程不存在${NC}"
    fi
    rm -f .frontend.pid
else
    echo -e "${YELLOW}⚠️  未找到前端 PID 文件${NC}"
fi

# 强制停止端口占用（备用方案）
echo -e "${YELLOW}🔍 检查端口占用...${NC}"

# 检查 5000 端口（后端）
BACKEND_PORT_PID=$(lsof -ti:5000 2>/dev/null || echo "")
if [ -n "$BACKEND_PORT_PID" ]; then
    kill -9 $BACKEND_PORT_PID 2>/dev/null || true
    echo -e "${GREEN}✓ 已释放 5000 端口${NC}"
fi

# 检查 5173 端口（前端）
FRONTEND_PORT_PID=$(lsof -ti:5173 2>/dev/null || echo "")
if [ -n "$FRONTEND_PORT_PID" ]; then
    kill -9 $FRONTEND_PORT_PID 2>/dev/null || true
    echo -e "${GREEN}✓ 已释放 5173 端口${NC}"
fi

echo -e "${GREEN}✓ 所有服务已停止${NC}"
