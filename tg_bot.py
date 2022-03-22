import logging

from environs import Env
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler


logger = logging.getLogger('tg_bot')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, chat_id, bot):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def button(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Selected option: {query.data}")


def start(update, context):
    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет']
    ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(text='Привет я бот для викторин!', reply_markup=reply_markup)


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
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, echo
    ))
    logger.info('Бот запущен!')
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
