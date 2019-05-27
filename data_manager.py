import connection
import util
import os
from psycopg2 import sql
from datetime import datetime


@connection.connection_handler
def get_questions(cursor):
    cursor.execute("""
                    SELECT * FROM question;
                   """)
    questions = cursor.fetchall()
    return questions



@connection.connection_handler
def get_question_by_id(cursor, question_id):
    cursor.execute("""
                    SELECT * FROM question
                    WHERE id = %(question_id)s;
                    """,
                   {'question_id': question_id})
    question = cursor.fetchone()
    return question


QUESTIONS_FILENAME = 'question.csv'
QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_FILENAME = 'answer.csv'
ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']



@connection.connection_handler
def get_answers_by_question_id(cursor, question_id):
    cursor.execute("""
                    SELECT * from answer
                    WHERE question_id=%(question_id_to_search)s;
                    """,
                   {'question_id_to_search': question_id})
    answers = cursor.fetchall()
    return answers


@connection.connection_handler
def add_question(cursor, user_question):
    timestamp = datetime.now()
    user_question['submission_time'] = timestamp
    cursor.execute("""
                    INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
                    VALUES (%(submission_time)s, 0, 0, %(title)s, %(message)s, %(image)s );
    """, user_question)


def add_answer(user_answer):
    answers = connection.read_csv(ANSWERS_FILENAME)

    new_answer = user_answer
    new_answer['id'] = new_id(ANSWERS_FILENAME)
    new_answer['submission_time'] = util.get_current_timestamp()
    new_answer['vote_number'] = 0

    answers.append(new_answer)
    connection.write_csv(answers, ANSWERS_FILENAME, ANSWERS_HEADER)


def delete_question_and_answers_by_id(question_id):
    questions = connection.read_csv(QUESTIONS_FILENAME)
    all_answers = connection.read_csv(ANSWERS_FILENAME)

    question_image = get_question_by_id(question_id)['image']
    delete_image(question_image)

    for question in questions:
        if question['id'] == question_id:
            questions.remove(question)
            break
    for answer in list(all_answers):
        if answer['question_id'] == question_id:
            delete_image(answer['image'])
            all_answers.remove(answer)

    connection.write_csv(questions, QUESTIONS_FILENAME, QUESTIONS_HEADER)
    connection.write_csv(all_answers, ANSWERS_FILENAME, ANSWERS_HEADER)


def delete_answer_by_id(answer_id):
    answers = connection.read_csv(ANSWERS_FILENAME)
    for answer in answers:
        if answer['id'] == answer_id:
            delete_image(answer['image'])
            answers.remove(answer)
            break
    connection.write_csv(answers, ANSWERS_FILENAME, ANSWERS_HEADER)


def delete_image(image):
    if image:
        os.remove('.' + image)


def new_id(filename):
    items = connection.read_csv(filename)
    max_id = max(int(item['id']) for item in items)    # generator expr. -> one iteration
    return max_id + 1


def edit_question(question_id, edited_question):
    questions = connection.read_csv(QUESTIONS_FILENAME)
    for question in questions:
        if question['id'] == question_id:
            question.update(edited_question)
    connection.write_csv(questions, QUESTIONS_FILENAME, QUESTIONS_HEADER)

@connection.connection_handler
def vote_question(cursor, question_id, vote):
    if vote == 'vote-up':
        cursor.execute("""
                    UPDATE question 
                    SET vote_number = vote_number + 1
                    WHERE id = %(question_id)s 
                    """,
                    {'question_id': question_id})
    elif vote == 'vote-down':
        cursor.execute("""
                    UPDATE question 
                    SET vote_number = vote_number - 1
                    WHERE id = %(question_id)s 
                    """,
                    {'question_id': question_id})



def vote_answer(answer_id, vote):
    answers = connection.read_csv(ANSWERS_FILENAME)
    if vote == 'vote-up':
        for answer in answers:
            if answer['id'] == answer_id:
                answer['vote_number'] = int(answer['vote_number']) + 1
    else:
        for answer in answers:
            if answer['id'] == answer_id:
                answer['vote_number'] = int(answer['vote_number']) - 1
    connection.write_csv(answers, ANSWERS_FILENAME, ANSWERS_HEADER)


def get_question_id_from_answer_id(answer_id):
    answers = connection.read_csv(ANSWERS_FILENAME)
    question_id = ''
    for answer in answers:
        if answer['id'] == answer_id:
            question_id = answer['question_id']
    return question_id
