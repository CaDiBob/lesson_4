import redis

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from environs import Env
from db import get_connect_db


def handle_new_question_request(event, vk_api, keyboard):
    db = context.bot_data['db']
    question = random.choice(list(
        context.bot_data['questions']
    ))
    update.message.reply_text(question, reply_markup=get_buttons())
    db.set(update.message.chat_id, question)


def send_reply_message(event, vk_api, keyboard):
    vk_api.messages.send(
        user_id=event.user_id,
        message='Привет я бот для викторин что бы начать нажми "Новый вопрос".',
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard()
    )


def main():
    env = Env()
    env.read_env('.env')
    db = get_connect_db()
    vk_token = env('VK_TOKEN')
    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться')
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text.lower() == 'start':
                send_reply_message(event, vk_api, keyboard)


if __name__ == "__main__":
    main()
