import json
import os
import re


def save_to_json(items):
    with open('quiz.json', 'w') as file:
        json.dump(items, file, indent=4, ensure_ascii=False)


def get_quiz_questions(file):
    quiz = list()
    for elem in file:
        one_quiz = dict()
        if re.search('Вопрос', elem):
            one_quiz.update(question=elem.split('\n'))
        if re.search('Ответ', elem):
            one_quiz.update(answer=elem.split('\n'))
        quiz.append(one_quiz)
    return list(filter(None, quiz))


def main():
    folder = 'quiz-questions'
    questions = sorted(os.listdir(folder))[0]
    with open(
            os.path.join(folder, questions), 'r', encoding='KOI8-R')as file:
        file = file.read()
    questions = file.split('\n\n')
    print(get_quiz_questions(questions))


if __name__ == '__main__':
    main()
