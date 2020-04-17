"""Lineからの入力メッセージを受け付ける機能を実装"""
# 組み込みモジュール
import os

# サードパーティ
import flask
import linebot
from flask import request, abort
from linebot import exceptions, models


app = flask.Flask(__name__)


# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = linebot.LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = linebot.WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route('/corona', methods=['POST'])
def corona():
    app.logger.info("START")

    signature = request.headers['X-Line-Signature']
    app.logger.info(signature)

    body = request.get_data(as_text=True)

    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except exceptions.InvalidSignatureError:
        abort(400)

    return 'OK'


@app.route('/', methods=['GET'])
def hello_world():
    return '<html>こんにちは</html>'


@handler.add(models.MessageEvent, message=models.TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        models.TextSendMessage(text=event.message.text))


if __name__ == '__main__':
    port = int(os.getenv('POST', 5000))
    app.run(port=port)
