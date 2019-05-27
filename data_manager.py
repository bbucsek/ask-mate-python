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

@connection.connection_handler
def add_answer(cursor, user_answer):
    timestamp = datetime.now()
    user_answer['submission_time'] = timestamp
    user_answer['question_id'] = int(user_answer['question_id'])
    cursor.execute("""
                    INSERT INTO answer (submission_time, vote_number, question_id, message, image)
                     VALUES (%(submission_time)s, 0, %(question_id)s, %(message)s, %(image)s)""",
                   user_answer)


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


@connection.connection_handler
def edit_question(cursor, id, edited_question):
    edited_question['id'] = id
    cursor.execute("""
                    UPDATE question
                    SET 
                        submission_time=CURRENT_TIMESTAMP,
                        title=%(title)s,
                        message=%(message)s
                    WHERE id=%(id)s;
                    """, edited_question)


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


@connection.connection_handler
def vote_answer(cursor, answer_id, vote):
    if vote == 'vote-up':
        cursor.execute("""
                    UPDATE answer 
                    SET vote_number = vote_number + 1
                    WHERE id = %(answer_id)s 
                    """,
               {'answer_id': answer_id})
    elif vote == 'vote-down':
        cursor.execute("""
                    UPDATE answer 
                    SET vote_number = vote_number - 1
                    WHERE id = %(answer_id)s 
                    """,
       {'answer_id': answer_id})



@connection.connection_handler
def get_question_id_by_answer_id(cursor, answer_id):
    cursor.execute("""
                    SELECT question_id FROM answer
                    WHERE id=%(answer_id)s;
                    """,
                   {'answer_id': answer_id})
    question_id = cursor.fetchone()
    return question_id['question_id']
