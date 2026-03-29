import os
import ssl
import certifi
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from dotenv import load_dotenv

import requests

os.environ['SSL_CERT_FILE'] = certifi.where()
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, FLASK_PORT, OPENROUTER_API_KEY, OPENROUTER_MODEL

load_dotenv()

app = Flask(__name__)
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

conversation_history = {}

def load_knowledge():
    files = ["data/knowledge.md", "data/products.md", "data/faqs.md"]
    content = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as file:
                content.append(file.read())
        except FileNotFoundError:
            pass
    return "\n\n".join(content)

KNOWLEDGE_BASE = load_knowledge()

SYSTEM_PROMPT = f"""你是「新鮮水果行」的友好助手，這是一間本地水果零售商。
你幫助顧客：
- 產品資訊和推薦
- 現有價格和優惠
- 水果食譜建議
- 訂購諮詢
- 水果相關問題

請使用繁體中文回覆。回答要簡潔且親切。如果顧客問到我們沒有販售的商品，請禮貌地說明我們目前的商品。

知識庫：
{KNOWLEDGE_BASE}"""

def get_ai_response(user_message, user_id):
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    if len(user_message) > 300:
        return "抱歉，訊息太長了，請分段傳送。"
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history[user_id])
    messages.append({"role": "user", "content": user_message})
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages,
        "max_tokens": 400,
        "temperature": 0.5
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        if "choices" not in result or not result["choices"]:
            return "抱歉，系統回應異常。"
        
        content = result["choices"][0].get("message", {}).get("content", "")
        if not content or len(content) < 2:
            return "抱歉，系統回應異常。"
        
        conversation_history[user_id].append({"role": "user", "content": user_message})
        conversation_history[user_id].append({"role": "assistant", "content": content})
        
        if len(conversation_history[user_id]) > 6:
            conversation_history[user_id] = conversation_history[user_id][-6:]
        
        return content
    except Exception as e:
        print(f"API Error: {e}")
        return "抱歉，系統忙碌中，請稍後再試。"

@app.route("/")
def index():
    return "LINE AI Bot running!"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent)
def handle_message(event):
    if isinstance(event.message, TextMessageContent):
        user_message = event.message.text
        user_id = event.source.user_id
        try:
            ai_response = get_ai_response(user_message, user_id)
        except:
            ai_response = "Sorry, I encountered an error. Please try again later."
        
        with ApiClient(configuration) as api_client:
            MessagingApi(api_client).reply_message(
                ReplyMessageRequest(
                    replyToken=event.reply_token,
                    messages=[TextMessage(text=ai_response)]
                )
            )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=FLASK_PORT,use_reloader=False, debug=True)
