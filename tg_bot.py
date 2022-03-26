import logging
import random

import redis
from environs import Env
import telegram
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
)
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
    ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    return reply_markup


def start(update, context):
    update.message.reply_text(text='Привет! Я бот для викторин.', reply_markup=get_buttons())


def get_answer(tg_user_id, context):
    db = context.bot_data['db']
    raw_answer = db.get(tg_user_id)
    answer, *_ = raw_answer.split('.')
    return answer.strip()


def get_give_up(update, context):
    tg_user_id = update.message.from_user['id']
    answer = get_answer(tg_user_id, context)
    update.message.reply_text(f'Ответ: {answer}', reply_markup=get_buttons())
    update.message.reply_text('Новый вопрос:')
    handle_new_question_request(update, context)


def handle_new_question_request(update, context):
    tg_user_id = update.message.from_user['id']
    questions = context.bot_data['questions']
    db = context.bot_data['db']
    question = random.choice(list(
        questions
    ))
    update.message.reply_text(question, reply_markup=get_buttons())
    db.set(tg_user_id, questions[question])


def handle_solution_attempt(update, context):
    tg_user_id = update.message.from_user['id']
    answer = get_answer(tg_user_id, context)
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
    db = redis.Redis(
        host=env('TG_REDIS_HOST'),
        port=env('TG_REDIS_PORT'),
        password=env('TG_REDIS_PASSWORD'),
        decode_responses=True,
    )
    tg_token = env('TG_TOKEN')
    tg_chat_id = env('TG_CHAT_ID')
    questions = get_questions_quiz()
    updater = Updater(tg_token)
    bot = telegram.Bot(token=tg_token)
    logger.addHandler(TelegramLogsHandler(tg_chat_id, bot))
    dispatcher = updater.dispatcher
    dispatcher.bot_data['db'] = db
    dispatcher.bot_data['questions'] = questions
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(
        Filters.regex(r'Новый вопрос'), handle_new_question_request
    ))
    dispatcher.add_handler(MessageHandler(
        Filters.regex(r'Сдаться'), get_give_up
    ))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, handle_solution_attempt
    ))
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
