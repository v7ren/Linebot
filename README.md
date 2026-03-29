#  LINE  AI客服

使用 LINE Messaging API 和 AI 生成式回覆的水果店聊天機器人。

## 功能特色

- AI 智能回覆 - 使用 OpenRouter API 驅動的 LLM 模型
- RAG 知識增強 - 從本地知識庫檢索相關資訊
- 記憶功能 - 支援多使用者對話記憶
- 水果商城情境 - 商品諮詢、價格查詢、常見問題

## 環境需求

- Python 3.10+
- LINE Developer 帳號
- OpenRouter API Key

## 安裝步驟

1. 複製專案
```bash
git clone <repository-url>
cd chatbot
```

2. 安裝依賴
```bash
pip install -r requirements.txt
```

3. 設定環境變數
```bash
cp .env.example .env
# 編輯 .env 填入您的 API Keys
```

4. 設定 LINE Bot
- 前往 [LINE Developers Console](https://developers.line.biz/)
- 建立 Messaging API 頻道
- 取得 Channel Access Token 和 Channel Secret
- 啟用 Webhook 並填入 `https://your-domain.com/callback`

5. 啟動服務
```bash
python main.py
```

## 環境變數說明

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Channel Access Token | 必填 |
| `LINE_CHANNEL_SECRET` | LINE Channel Secret | 必填 |
| `OPENROUTER_API_KEY` | OpenRouter API Key | 必填 |
| `OPENROUTER_MODEL` | AI 模型名稱 | meta-llama/llama-3.1-8b-instruct |
| `FLASK_PORT` | Flask 伺服器端口 | 3000 |
| `DATA_FOLDER` | 知識庫資料夾 | ./data |
| `EMBEDDING_MODEL` | 向量化模型 | all-MiniLM-L6-v2 |

## 知識庫目錄結構

```
data/
├── knowledge.md    # 商店資訊
├── products.md     # 商品目錄
├── faqs.md         # 常見問題
└── documents.json # 預處理文檔（可選）
```

## 自訂知識庫

編輯 `data/` 目錄下的 `.md` 檔案即可更新 AI 的知識儲備。

## 部署建議

- 使用 gunicorn 或 uwsgi 作為生產環境 WSGI 伺服器
- 建議使用 Nginx 反向代理
- 確保 Webhook URL 為 HTTPS

## 授權

MIT License
