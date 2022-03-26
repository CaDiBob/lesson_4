import random

import redis
from time import sleep
import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from environs import Env
from questions import get_questions_quiz


def get_answer(event, db):
    questions = get_questions_quiz()
    question = db.get(event.user_id)
    answer, *trash = questions[question].split('.')
    return answer.strip()


def get_give_up(event, vk_api, db):
    answer = get_answer(event, db)
    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Ответ: {answer}',
        random_id=get_random_id(),
        keyboard=get_keyboard(),
    )
    sleep(1)
    vk_api.messages.send(
        user_id=event.user_id,
        message='Новый вопрос:',
        random_id=get_random_id(),
        keyboard=get_keyboard(),
    )
    handle_new_question_request(event, vk_api, db)


def handle_solution_attempt(event, vk_api, db):
    answer = get_answer(event, db)
    text = event.text
    if text == answer:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            random_id=get_random_id(),
            keyboard=get_keyboard()
        )
    if text != answer:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Неправильно… Попробуешь ещё раз?',
            random_id=get_random_id(),
            keyboard=get_keyboard()
        )


def handle_new_question_request(event, vk_api, db):
    question = random.choice(list(
        get_questions_quiz()
    ))
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=get_random_id(),
        keyboard=get_keyboard()
    )
    db.set(event.user_id, question)


def start(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message='Привет я бот для викторин что бы начать нажми "Новый вопрос".',
        random_id=get_random_id(),
        keyboard=get_keyboard()
    )


def get_keyboard():
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться')
    return keyboard.get_keyboard()


def main():
    env = Env()
    env.read_env('.env')
    db = redis.Redis(
        host=env('REDIS_HOST'),
        port=env('REDIS_PORT'),
        password=env('REDIS_PASSWORD'),
        decode_responses=True,
    )
    vk_token = env('VK_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text.lower() == 'start':
                start(event, vk_api)
            elif event.text == 'Новый вопрос':
                handle_new_question_request(event, vk_api, db)
            elif event.text == 'Сдаться':
                get_give_up(event, vk_api, db)
            else:
                handle_solution_attempt(event, vk_api, db)


if __name__ == "__main__":
    main()
