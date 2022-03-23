import os
import re
import random


def get_questions_quiz():
    question_quiz = dict()
    folder = 'quiz-questions'
    questions_file = sorted(os.listdir(folder))
    for txt_file in questions_file:
        with open(
                os.path.join(folder, txt_file), 'r', encoding='KOI8-R')as file:
            file = file.read()
        questions = file.split('\n\n\n')
        for question in questions:
            question_and_answer = question.split('\n\n')
            for text in question_and_answer:
                if re.findall('Вопрос.*:', text):
                    question_text = re.split('Вопрос.*:', text)[1]
                    question_text = question_text.replace('\n', ' ')
                if re.findall('Ответ:', text):
                    answer_text = re.split('Ответ:', text)[1]
                    answer_text = answer_text.replace('\n', ' ')
            question_quiz[question_text] = answer_text
    return question_quiz


if __name__ == '__main__':
    print(random.choice(list(get_questions_quiz().keys())))