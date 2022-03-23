import logging
import random

from environs import Env
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from questions import get_questions_quiz


logger = logging.getLogger('tg_bot')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, chat_id, bot):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def get_buttons():
    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет']
    ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    return reply_markup


def start(update, context):
    update.message.reply_text(text='Привет! Я бот для викторин.', reply_markup=get_buttons())


def get_new_question(update, context):
    questions = get_questions_quiz()
    question = random.choice(list(questions.keys()))
    update.message.reply_text(question, reply_markup=get_buttons())


def get_give_up(update, context):
    pass


def get_answer(update, context):
    pass


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
    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(Filters.regex(r'Новый вопрос'), get_new_question),
            MessageHandler(Filters.regex(r'Сдаться'), get_give_up),
            MessageHandler(Filters.text & ~Filters.command, get_answer),
        ],
        states={},
        fallbacks=[])
    dispatcher.add_handler(conversation_handler)
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
