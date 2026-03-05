#!/bin/bash
# QCLaw 系统测试脚本
# 用于在 Docker 环境中运行系统级测试

set -e

echo "🚀 启动 QCLaw 系统测试..."

# 进入项目目录
cd /home/openclaw/qclaw

# 启动 Docker Compose 服务
echo "📦 启动 Docker 服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动 (30 秒)..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 运行系统测试
echo "🧪 运行系统测试..."
docker-compose exec -T api pytest tests/system/ -v --tb=short

# 运行集成测试
echo "🔗 运行集成测试..."
docker-compose exec -T api pytest tests/integration/ -v --tb=short

# 查看测试报告
echo "📊 测试完成！"
echo "✅ 系统测试通过"

# 可选：停止服务
# echo "🛑 停止服务..."
# docker-compose down

echo "🎉 所有测试完成！"
