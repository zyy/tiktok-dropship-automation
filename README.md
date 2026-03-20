# TikTok 无货源带货自动化系统

[![GitHub Actions](https://github.com/zyy/tiktok-dropship-automation/actions/workflows/automation.yml/badge.svg)](https://github.com/zyy/tiktok-dropship-automation/actions/workflows/automation.yml)

全自动化的跨境电商带货系统，流程如下：

```
TikTok热门商品搜索 → 亚马逊商品匹配 → AI生成带货视频 → TikTok自动发布
```

## ✨ 核心功能

- ✅ **TikTok热门商品抓取** - 自动发现美区热门商品和趋势标签
- ✅ **亚马逊商品匹配** - 搜索相似商品、获取图片、计算利润
- ✅ **AI视频生成** - GPT-4生成脚本 + TTS配音 + 视频合成
- ✅ **TikTok自动发布** - API发布 / Selenium模拟发布
- ✅ **定时自动化** - GitHub Actions定时运行

## 📦 项目结构

```
tiktok-dropship-automation/
├── main.py                    # 主程序入口
├── requirements.txt           # Python依赖
├── .env.example              # 环境变量模板
├── README.md                 # 项目说明
├── tiktok_scraper/           # TikTok热门商品爬取
│   └── scraper.py
├── amazon_scraper/           # 亚马逊商品匹配
│   └── scraper.py
├── ai_video_generator/       # AI视频生成
│   └── generator.py
├── tiktok_publisher/         # TikTok自动发布
│   └── publisher.py
└── .github/workflows/        # GitHub Actions定时任务
    └── automation.yml
```

## 🚀 快速开始

### 1. 安装依赖

```bash
git clone https://github.com/zyy/tiktok-dropship-automation.git
cd tiktok-dropship-automation
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 3. 运行

```bash
# 单个商品模式
python main.py --single "Wireless Bluetooth Earbuds"

# 批量模式（默认处理3个商品）
python main.py --batch 5

# 定时模式（每6小时运行）
python main.py --schedule --interval 6
```

## ⚙️ 配置说明

### 必需的 API 密钥

| 变量名 | 说明 | 获取方式 |
|--------|------|---------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `TIKTOK_ACCESS_TOKEN` | TikTok API 令牌 | [TikTok Developers](https://developers.tiktok.com/) |
| `TIKTOK_OPEN_ID` | TikTok 用户 ID | TikTok API |

### 可选配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `OUTPUT_DIR` | `./output` | 输出目录 |
| `TEMP_DIR` | `./temp` | 临时文件目录 |

## 🔄 GitHub Actions 自动化

### 配置 Secrets

1. 进入仓库 Settings → Secrets and variables → Actions
2. 添加以下 Secrets：
   - `OPENAI_API_KEY`
   - `TIKTOK_ACCESS_TOKEN`
   - `TIKTOK_OPEN_ID`

详细配置请参考 [.github/workflows/README.md](.github/workflows/README.md)

### 运行方式

- **自动运行**: 每天北京时间 20:00（美区早上 8:00）
- **手动触发**: Actions 页面 → Run workflow

## 📊 运行示例

```json
{
  "success": true,
  "tiktok_product": {
    "name": "Wireless Bluetooth Earbuds",
    "views": 1000000,
    "trending_score": 8.5
  },
  "amazon_product": {
    "title": "Bluetooth Earbuds with Noise Cancelling",
    "price": 35.99,
    "rating": 4.5
  },
  "video": {
    "title": "Stop scrolling! You need to see this...",
    "duration": 40,
    "hashtags": ["#tiktokmademebuyit", "#amazonfinds"]
  },
  "publish_result": {
    "success": true,
    "video_id": "mock_123456",
    "url": "https://tiktok.com/@user/video/123456"
  }
}
```

## 🛠️ 技术栈

- **Python 3.11+**
- **OpenAI GPT-4** - 脚本生成
- **OpenAI TTS** - 语音合成
- **Playwright/Selenium** - 浏览器自动化
- **TikTok API** - 视频发布
- **GitHub Actions** - 定时任务

## 📝 注意事项

1. **TikTok API 限制**: 需要申请 TikTok for Developers 账号
2. **OpenAI 费用**: GPT-4 和 TTS 会产生 API 调用费用
3. **合规性**: 请遵守 TikTok 和 Amazon 的服务条款
4. **视频内容**: 建议人工审核后再发布

## 📜 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
