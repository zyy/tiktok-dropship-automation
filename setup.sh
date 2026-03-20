#!/bin/bash

echo "================================"
echo "TikTok Dropship Automation Setup"
echo "================================"

# 创建 .env 文件
echo "Creating .env file..."

cat > .env << 'EOF'
# OpenAI API 密钥 (从 https://platform.openai.com/api-keys 获取)
OPENAI_API_KEY=sk-your-openai-api-key-here

# TikTok API 配置 (从 https://developers.tiktok.com 获取)
TIKTOK_ACCESS_TOKEN=your_tiktok_access_token
TIKTOK_OPEN_ID=your_tiktok_open_id

# TikTok 账号（可选，用于Selenium模式）
TIKTOK_USERNAME=your_tiktok_username
TIKTOK_PASSWORD=your_tiktok_password

# 目录配置
OUTPUT_DIR=./output
TEMP_DIR=./temp

# 日志配置
LOG_LEVEL=INFO
EOF

echo ".env file created!"

# 安装 Python 依赖
echo "Installing dependencies..."
pip install -r requirements.txt

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "接下来需要手动完成："
echo "1. 打开 .env 文件"
echo "2. 替换 API 密钥："
echo "   - OPENAI_API_KEY: 你的 OpenAI API 密钥"
echo "   - TIKTOK_ACCESS_TOKEN: TikTok API 令牌"
echo "   - TIKTOK_OPEN_ID: TikTok 用户 Open ID"
echo ""
echo "3. 配置 GitHub Secrets："
echo "   - 访问 https://github.com/zyy/tiktok-dropship-automation/settings/secrets/actions"
echo "   - 添加与 .env 相同的密钥"
echo ""
echo "4. 测试运行："
echo "   python main.py --single 'Wireless Bluetooth Earbuds'"