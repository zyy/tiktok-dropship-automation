# GitHub Actions Secrets 配置指南

## 配置步骤

1. 打开仓库设置页面：
   https://github.com/zyy/tiktok-dropship-automation/settings/secrets/actions

2. 点击 **New repository secret** 添加以下 Secrets：

### 必需 Secrets

| Secret Name | 说明 | 获取方式 |
|------------|------|---------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | https://platform.openai.com/api-keys |
| `TIKTOK_ACCESS_TOKEN` | TikTok API 访问令牌 | TikTok for Developers |
| `TIKTOK_OPEN_ID` | TikTok 用户 Open ID | TikTok for Developers |

### 可选 Secrets

| Secret Name | 说明 |
|------------|------|
| `TIKTOK_USERNAME` | TikTok 用户名（用于 Selenium 模式） |
| `TIKTOK_PASSWORD` | TikTok 密码（用于 Selenium 模式） |

## 获取 API 密钥

### OpenAI API Key
1. 访问 https://platform.openai.com/
2. 登录账号 → API keys → Create new secret key
3. 复制密钥并添加到 GitHub Secrets

### TikTok API 凭证
1. 访问 https://developers.tiktok.com/
2. 创建应用并获取 Access Token
3. 参考文档：https://developers.tiktok.com/doc/overview

## 运行工作流

### 方式1：自动定时运行
- 每天北京时间 20:00 自动运行
- 处理 3 个热门商品

### 方式2：手动触发
1. 进入 Actions 页面
2. 选择 "TikTok Dropship Automation"
3. 点击 "Run workflow"
4. 选择模式：
   - **batch**: 批量模式（默认处理3个商品）
   - **single**: 单个商品模式（需输入关键词）

## 查看结果

运行完成后：
1. 在 Actions 页面查看运行日志
2. 在 Artifacts 中下载生成的视频和日志
3. 视频保留 7 天后自动删除

## 注意事项

- 免费版 GitHub Actions 每月有 2000 分钟限制
- 每次运行约 5-15 分钟（取决于视频生成数量）
- 建议将 `TIKTOK_ACCESS_TOKEN` 设置为不过期或定期更新
