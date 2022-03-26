import os
import re


def get_questions_quiz():
    questions_quiz = dict()
    folder = 'quiz-questions'
    question_files = sorted(os.listdir(folder))
    for questions_file in question_files:
        with open(
                os.path.join(folder, questions_file), 'r', encoding='KOI8-R')as file:
            file = file.read()
        questions = file.split('\n\n\n')
        for question in questions:
            raw_texts = question.split('\n\n')
            for text in raw_texts:
                if re.findall(r'Вопрос.*:', text):
                    question_text = re.split(r'Вопрос.*:', text)[1]
                    question_text = question_text.replace('\n', ' ')
                if re.findall(r'Ответ:', text):
                    answer_text = re.split(r'Ответ:', text)[1]
                    answer_text = answer_text.replace('\n', ' ')
            questions_quiz[question_text] = answer_text
    return questions_quiz
