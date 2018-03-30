import os
import sys
from argparse import ArgumentParser
from random import sample

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)


TEAM_SYMBOLS = ('RED', 'YELLOW', 'BLUE', 'GREEN')
HELP_MESSAGE = (
    'できること:\n'
    'チーム分け: チーム 10\n'
    '　10人を2チームに分けます\n'
    'スパイ戦: スパイ 10 1\n'
    '　10人を2チームに分けます。\n'
    '　チームごとに1人ずつのスパイを配役します'
    )


app = Flask(__name__)

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    print(event)
    text = event.message.text
    reply = None
    if 'できること' in text:
        reply = HELP_MESSAGE
    elif text.startswith('チーム'):
        reply = get_grouping(text)
    elif text.startswith('スパイ'):
        reply = get_casting_spy(text)

    print(reply)

    if not reply:
        return

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


def grouping(all_num):
    team_num = 2
    member_num = all_num // team_num
    member_list = sample(range(1, all_num+1), all_num)
    group_list = (
        list(map(str, sorted(member_list[:member_num]))),
        list(map(str, sorted(member_list[member_num:]))),
        )
    return group_list


def get_grouping(text):
    # 'チーム 10(全員の人数)'などとする
    try:
        _, all_num = text.split()
    except ValueError:
        return '「チーム 10」のようにスペースを空けて入力してください'
    group_list = grouping(int(all_num))

    reply = ''
    for symbol, group in zip(TEAM_SYMBOLS, group_list):
        reply += (
            '===== {} =====\n'
            '{}\n'
        ).format(
            symbol,
            ', '.join(group),
        )
    return reply


def get_casting_spy(text):
    # 'スパイ 10(全員の人数) 2(チームごとのスパイの人数)'などとする
    try:
        _, all_num, spy_num = text.split()
    except ValueError:
        return '「スパイ 10 2」のようにスペースを空けて入力してください'
    group_list = grouping(int(all_num))
    spy_num = int(spy_num)

    reply = ''
    for symbol, group in zip(TEAM_SYMBOLS, group_list):
        spy = sample(group, spy_num)
        reply += (
            '===== {} =====\n'
            '{}\n'
            'spy: {}\n'
        ).format(
            symbol,
            ', '.join(group),
            ', '.join(spy),
        )
    return reply


if __name__ == "__main__":
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
