from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageMessage,AudioMessage,ImageSendMessage
)
import makeCol_v2
import os



app = Flask(__name__)

# 環境変数からchannel_secret・channel_access_tokenを取得
#channel_secret = os.environ['LINE_CHANNEL_SECRET']
#channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
channel_secret = 'e242c61890a3d8a19e16f9b3aa086c0c'
channel_access_token = 'bJxpyvj91Cl7WyL1lpRvZL0Jsiw5UPvPV+hI+Ol8fxX2G8dy9s8GGEDUC9pHkepDW7wG+8AT6PcqVM8L8cGpRFArvuXqGuqvPqTcnVgrafh6//98ggTIziMItg7vwKJeDfxYzFuYjsb5kJ2UcHi2CAdB04t89/1O/w1cDnyilFU='


line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/")
def hello_world():
    return "hello world!"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    #app.logger.info("Request body: " + body)
    print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=(TextMessage,AudioMessage))
def handle_text_message(event):
    #reply = '画像を送ってください'
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="津田の趣味です")
        #ImageSendMessage(
        #        original_content_url='https://s3.ap-northeast-1.amazonaws.com/accept-image/tsuda.jpg',
        #        preview_image_url='https://s3.ap-northeast-1.amazonaws.com/accept-image/tsuda.jpg'
        #)
        )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    messageID = event.message.id
    message_content = line_bot_api.get_message_content(messageID)
    print('バイナリ確認')
    print(message_content)
    #画像保存
    srcName = 'testpy.jpg'
    with open(srcName, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
    msg,completeFlg = makeCol_v2.makeImage(srcName)
    if completeFlg:
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(
                original_content_url='https://s3-ap-northeast-1.amazonaws.com/accept-image/masked_result.jpg',
                preview_image_url='https://s3-ap-northeast-1.amazonaws.com/accept-image/masked_result.jpg'
            )
            )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg)
            )

if __name__ == "__main__":
    app.run()
