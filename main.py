"""Lineからの入力メッセージを受け付ける機能を実装"""
# 組み込みモジュール
import os

# サードパーティ
import flask
import linebot
from flask import request, abort
from linebot import exceptions, models

# 自作モジュール
from collector import infected_person

app = flask.Flask(__name__)


# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ['YOUR_CHANNEL_ACCESS_TOKEN']
YOUR_CHANNEL_SECRET = os.environ['YOUR_CHANNEL_SECRET']

line_bot_api = linebot.LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = linebot.WebhookHandler(YOUR_CHANNEL_SECRET)

text = """\
キーワードにマッチする情報が見つけれらませんでした。<(_ _)>"""


@app.route('/corona', methods=['POST'])
def receptionist():

    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)

    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except exceptions.InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(models.MessageEvent, message=models.TextMessage)
def handle_message(event):

    # nippon.comのwebサイトから日本国内の感染者情報を取得
    ip = infected_person.NipponComSite()
    hit_word = ip.searcher(event.message.text)
    if not hit_word:
        hit_word = text

    line_bot_api.reply_message(
        event.reply_token,
        models.TextSendMessage(text=hit_word))


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
