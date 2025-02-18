#!/bin/bash
echo "正在启动 SFpanel..."

# 启动后端服务
cd "$(dirname "$0")"
python main.py &

# 等待2秒确保后端启动
sleep 2

# 启动前端服务
cd frontend
npm run dev &

echo "SFpanel 启动完成！"