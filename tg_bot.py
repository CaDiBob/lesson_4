import logging

from environs import Env
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


logger = logging.getLogger('tg_bot')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, chat_id, bot):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def start(update, context):
    update.message.reply_text('Добро пожаловать!')


def help(update, context):
    update.message.reply_text(
        '''
        Бот по проведению викторины на должность смотрителя музея!
        '''
    )


def echo(update, context):
    update.message.reply_text(update.message.text)


def error(update, context):
    logger.error(context.error)


def main():
    env = Env()
    env.read_env()
    tg_token = env('TG_TOKEN')
    tg_chat_id = env('TG_CHAT_ID')
    updater = Updater(tg_token)
    bot = telegram.Bot(token=tg_token)
    logger.addHandler(TelegramLogsHandler(tg_chat_id, bot))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo
    ))
    logger.info('Бот запущен!')
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
