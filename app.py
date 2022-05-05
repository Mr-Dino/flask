from flask import Flask, jsonify, request, make_response, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database


from config import DATABASE, HOST, PORT, USERNAME, PASSWORD, QUIZ_URL
from models import Quiz


import requests


app = Flask(__name__)


def main(questions_quantity):
    """
    Главная функция
    1. Подключается к БД
    2. Выполняет внесение данных и сохранение их в БД
    """
    url = f'postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
    if not database_exists(url):
        create_database(url)
    engine = create_engine(url)
    Session = sessionmaker(bind=engine)
    session = Session()
    take_data(questions_quantity, session)


@app.route('/question_num/api/', methods=['GET', 'POST'])
def get_question_num():
    """Функция получения кол-ва вопросов"""
    if not request.json:
        abort(404)
    elif request.json['question_num'].isnumeric():
        abort(404)
    questions_quantity = int(request.json['question_num'])
    main(questions_quantity)
    return


@app.errorhandler(404)
def not_found_error(error):
    """Обработка  ошибки 404"""
    return make_response(jsonify({'error': 'Not found'}), 404)


def take_data(count, session):
    """Внесение данных, полученных в запросе в БД"""
    new_data = make_request(count)
    all_ids = get_all_ids(session)
    for item in new_data:
        id = item['id']
        while checkout(all_ids, id):
            item = make_request(1)[0]
            id = item['id']
        all_ids.append(item['id'])
        new_quiz = Quiz(id=item['id'], question_text=item['question'], answer=item['answer'], date=item['airdate'])
        session.add(new_quiz)
        session.commit()


def checkout(all_ids, id):
    """Функция для проверки существует ли в БД вопрос с таким же ID"""
    if id in all_ids:
        return True
    else:
        return False


def get_all_ids(session):
    """Получение всех ID из БД"""
    all_ids = []
    for quiz in session.query(Quiz):
        all_ids.append(quiz.id)
    return all_ids


def make_request(count):
    """Создание запроса для получения вопросов (с параметром кол-ва вопросов)"""
    count = str(count)
    url = QUIZ_URL + count
    response = requests.get(url)
    return response.json()


if __name__ == '__main__':
    app.run(debug=True)
