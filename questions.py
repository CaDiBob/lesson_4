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
            question_and_answer = question.split('\n\n')
            for text in question_and_answer:
                if re.findall('Вопрос.*:', text):
                    question_text = re.split('Вопрос.*:', text)[1]
                    question_text = question_text.replace('\n', ' ')
                if re.findall('Ответ:', text):
                    answer_text = re.split('Ответ:', text)[1]
                    answer_text = answer_text.replace('\n', ' ')
            questions_quiz[question_text] = answer_text
    return questions_quiz
