import logging
import random
from time import sleep

from environs import Env
import redis
import telegram
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
)
from questions import get_questions_quiz
from db import get_connect_db


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
    ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    return reply_markup


def start(update, context):
    update.message.reply_text(text='Привет! Я бот для викторин.', reply_markup=get_buttons())


def get_answer(update, context):
    questions = context.bot_data['questions']
    db = context.bot_data['db']
    question = db.get(update.message.chat_id)
    answer, *trash = questions[question].split('.')
    return answer.strip()


def get_give_up(update, context):
    answer = get_answer(update, context)
    update.message.reply_text(f'Ответ: {answer}', reply_markup=get_buttons())
    sleep(1)
    update.message.reply_text('Новый вопрос:')
    handle_new_question_request(update, context)


def handle_new_question_request(update, context):
    db = context.bot_data['db']
    question = random.choice(list(
        context.bot_data['questions']
    ))
    update.message.reply_text(question, reply_markup=get_buttons())
    db.set(update.message.chat_id, question)


def handle_solution_attempt(update, context):
    answer = get_answer(update, context)
    text = update.message.text
    if text == answer:
        update.message.reply_text(
            'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            reply_markup=get_buttons(),
        )
    else:
        update.message.reply_text(
            'Неправильно… Попробуешь ещё раз?',
        )


def error(update, context):
    logger.error(context.error)


def main():
    env = Env()
    env.read_env()
    db = get_connect_db()
    tg_token = env('TG_TOKEN')
    tg_chat_id = env('TG_CHAT_ID')
    questions = get_questions_quiz()
    updater = Updater(tg_token)
    bot = telegram.Bot(token=tg_token)
    logger.addHandler(TelegramLogsHandler(tg_chat_id, bot))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.bot_data['db'] = db
    dispatcher.bot_data['questions'] = questions
    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(Filters.regex(r'Новый вопрос'), handle_new_question_request),
            MessageHandler(Filters.regex(r'Сдаться'), get_give_up),
            MessageHandler(Filters.text & ~Filters.command, handle_solution_attempt),
        ],
        states={},
        fallbacks=[])
    dispatcher.add_handler(conversation_handler)
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
