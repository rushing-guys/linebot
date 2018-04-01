import os
import sys
from argparse import ArgumentParser


from linebot import LineBotApi
from linebot.models import TextSendMessage


if __name__ == '__main__':
    spacer = ' ' * len('usage: python ' + __file__)
    arg_parser = ArgumentParser(
        usage=(
            f'python {__file__} [--access-token <access-token>]\n'
            f'{spacer} [--to <to>][--message <message>]\n'
            f'{spacer} [--help]\n'
            )
        )
    arg_parser.add_argument('-a', '--access-token', help='アクセストークン')
    arg_parser.add_argument('-t', '--to-id', help='送り先ID')
    arg_parser.add_argument('-m', '--message', help='メッセージ')
    options = arg_parser.parse_args()

    # コマンドライン引数の方が高優先度
    access_token = options.access_token or os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    if access_token is None:
        print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
        sys.exit(1)
    line_bot_api = LineBotApi(access_token)

    to_id = options.to_id or os.getenv('TO_ID')
    if to_id and options.message:
        line_bot_api.push_message(
            to_id,
            TextSendMessage(text=options.message)
        )
    else:
        print('need "to-id" and "message"')
