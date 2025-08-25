import os
import openai
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 環境変数の設定（Renderでは管理画面で設定）
openai.api_key = os.environ["OPENAI_API_KEY"]
line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

# プロンプト（語り部の声）
my_prompt_text = """
[ナレーション]
「今、まさに歴史の扉を開けるのですね、社長。
その一歩が、あなたの未来を変えるかもしれません。
...（省略可）...
"""

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    combined_message = my_prompt_text + "\n\nユーザーからのメッセージ: " + user_message

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたは、社長の物語を紐解く語り部です。"},
            {"role": "user", "content": combined_message}
        ]
    )
    ai_reply = response["choices"][0]["message"]["content"]

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ai_reply[:1000])
    )

@app.route("/health")
def health():
    return "OK", 200

@app.route("/", methods=["GET"])
def index():
    return "LINE Bot is running, 社長！"
