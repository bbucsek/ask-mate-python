import connection
import os
import psycopg2
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


@connection.connection_handler
def get_answers_by_question_id(cursor, question_id):
    cursor.execute("""
                    SELECT * from answer
                    WHERE question_id=%(question_id_to_search)s;
                    """,
                   {'question_id_to_search': question_id})
    answers = cursor.fetchall()
    return answers


def get_answers_with_comments_by_question_id(question_id):
    answers = get_answers_by_question_id(question_id)
    for answer in answers:
        answer['comments'] = get_comments_from_answer_id(answer['id'])
    return answers


@connection.connection_handler
def add_question(cursor, user_question, user_id):
    timestamp = datetime.now()
    user_question['submission_time'] = timestamp
    user_question['user_id'] = user_id
    cursor.execute("""
                    INSERT INTO question (submission_time, view_number, vote_number, title, message, image, user_id)
                    VALUES (%(submission_time)s, 0, 0, %(title)s, %(message)s, %(image)s, %(user_id)s );
    """, user_question)


@connection.connection_handler
def add_answer(cursor, user_answer, user_id):
    timestamp = datetime.now()
    user_answer['submission_time'] = timestamp
    user_answer['user_id'] = user_id
    user_answer['question_id'] = int(user_answer['question_id'])
    cursor.execute("""
                    INSERT INTO answer (submission_time, vote_number, question_id, message, image, user_id)
                     VALUES (%(submission_time)s, 0, %(question_id)s, %(message)s, %(image)s, %(user_id)s)""",
                   user_answer)


def delete_question_and_answers_by_id(question_id):
    answers_to_delete = get_answers_by_question_id(question_id)
    for answer in answers_to_delete:
        delete_answer_by_id(answer['id'])
        delete_image(answer['image'])

    delete_question_by_id(question_id)


@connection.connection_handler
def delete_question_by_id(cursor, question_id):
    comments = get_comments_from_question_id(question_id)
    for comment in comments:
        delete_comment_by_id(comment['id'])
    question_image = get_question_by_id(question_id)['image']
    cursor.execute("""
                    DELETE
                    FROM question
                    WHERE id=%(question_id)s;
                    """,
                   {'question_id': question_id})
    delete_image(question_image)


def delete_answer_with_image_by_id(answer_id):
    image = get_image_by_answer_id(answer_id)
    delete_answer_by_id(answer_id)
    delete_image(image)


@connection.connection_handler
def delete_answer_by_id(cursor, answer_id):
    comments = get_comments_from_answer_id(answer_id)
    for comment in comments:
        delete_comment_by_id(comment['id'])

    cursor.execute("""
                    DELETE
                    FROM answer
                    WHERE id=%(answer_id)s;
                    """,
                   {'answer_id': answer_id})


@connection.connection_handler
def get_image_by_answer_id(cursor, answer_id):
    cursor.execute("""
                    SELECT image
                    FROM answer
                    WHERE id=%(answer_id)s;
                    """,
                   {'answer_id': answer_id})
    image = cursor.fetchone()
    return image['image'] if image else None


@connection.connection_handler
def search_for_image_usage(cursor, image):
    cursor.execute("""
                    SELECT id FROM answer
                    WHERE image=%(image)s
                    UNION ALL
                    SELECT id FROM question
                    WHERE image=%(image)s
                    """,
                   {'image': image})
    is_used = cursor.rowcount > 0
    return is_used


def delete_image(image):
    if image:
        is_used = search_for_image_usage(image)
        if not is_used:
            os.remove('.' + image)


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


@connection.connection_handler
def get_answer_by_answer_id(cursor, answer_id):
    cursor.execute("""
                    SELECT * 
                    FROM answer
                    WHERE id=%(answer_id)s;
                    """,
                   {'answer_id': answer_id})
    return cursor.fetchone()


@connection.connection_handler
def get_question_by_answer_id(cursor, answer_id):
    cursor.execute("""
                    SELECT question.*
                    FROM answer, question
                    WHERE 
                        answer.id=%(answer_id)s
                        AND question.id=answer.question_id;
                    """,
                   {'answer_id': answer_id})
    question = cursor.fetchone()
    return question

@connection.connection_handler
def get_question_by_search(cursor, search):
    searched_text = '%'+ search + '%'
    cursor.execute("""
                    SELECT DISTINCT question.*
                    FROM question, answer
                    WHERE question.title ILIKE %(searched_text)s
                    OR  question.message ILIKE %(searched_text)s
                    OR (answer.message ILIKE %(searched_text)s
                    AND answer.question_id=question.id);
                    """,
                   {'searched_text': searched_text})
    result = cursor.fetchall()
    return result



@connection.connection_handler
def add_comment_to_answer(cursor, answer_id, message, user_id):
    cursor.execute("""
                    INSERT INTO comment (answer_id, message, submission_time, edited_count, user_id)
                    VALUES (%(answer_id)s, %(message)s, CURRENT_TIMESTAMP, 0, %(user_id)s);
                    """,
                    {'answer_id': answer_id, 'message': message, 'user_id': user_id})


@connection.connection_handler
def edit_question(cursor, edited_question):
    edited_question = handle_new_image(edited_question)
    cursor.execute("""
                    UPDATE question
                    SET 
                        submission_time=CURRENT_TIMESTAMP,
                        title=%(title)s,
                        message=%(message)s,
                        image=%(image)s
                    WHERE id=%(id)s;
                    """, edited_question)


@connection.connection_handler
def edit_answer(cursor, edited_answer):
    edited_answer = handle_new_image(edited_answer)
    cursor.execute("""
                    UPDATE answer
                    SET message=%(message)s,
                        image=%(image)s
                    WHERE id=%(id)s;
                    """, edited_answer)


def handle_new_image(edited):
    if edited.get('old_image'):
        if edited.get('image'):
            delete_image(edited['old_image'])
        else:
            edited['image'] = edited['old_image']
    return edited


@connection.connection_handler
def add_comment_to_question(cursor, question_id, user_comment, user_id):
    timestamp = datetime.now()
    user_comment['submission_time'] = timestamp
    user_comment['question_id'] = question_id
    user_comment['user_id'] = user_id
    cursor.execute("""
                    INSERT INTO comment (question_id, submission_time, message, edited_count, user_id)
                    VALUES (%(question_id)s, %(submission_time)s, %(message)s, 0, %(user_id)s);
    """, user_comment)


@connection.connection_handler
def get_comments_from_question_id(cursor, question_id):
    cursor.execute("""
                    SELECT *
                    FROM comment
                    WHERE 
                        question_id=%(question_id)s
                    """,
                   {'question_id': question_id})
    comments = cursor.fetchall()
    return comments


@connection.connection_handler
def get_comments_from_answer_id(cursor, answer_id):
    cursor.execute("""
                    SELECT *
                    FROM comment
                    WHERE 
                        answer_id=%(answer_id)s
                    ORDER BY submission_time DESC
                    """,
                   {'answer_id': answer_id})
    comments = cursor.fetchall()
    return comments


@connection.connection_handler
def delete_comment_by_id(cursor, comment_id):
    cursor.execute("""
                    DELETE
                    FROM comment
                    WHERE id=%(comment_id)s;
                    """,
                   {'comment_id': comment_id})



@connection.connection_handler
def get_comment_by_id(cursor, comment_id):
    cursor.execute("""
                    SELECT *
                    FROM comment
                    WHERE id = %(comment_id)s;
                    """,
                   {'comment_id': comment_id})
    return cursor.fetchone()


def get_question_id_by_comment_id(comment_id):
    comment = get_comment_by_id(comment_id)
    if comment['question_id'] is None:
        return get_question_id_by_answer_id(comment['answer_id'])
    else:
        return comment['question_id']


@connection.connection_handler
def edit_comment(cursor, comment_id, new_message, edited_count):
    cursor.execute("""
                    UPDATE comment
                    SET message=%(message)s,
                        submission_time=CURRENT_TIMESTAMP,
                        edited_count=%(edited_count)s
                    WHERE id=%(comment_id)s
                    """,
                   {'comment_id': comment_id, 'message': new_message, 'edited_count': edited_count})


@connection.connection_handler
def get_latest_five_questions(cursor):
    cursor.execute("""
                    SELECT * FROM question
                    ORDER BY id DESC
                    LIMIT 5;
                   """)
    questions = cursor.fetchall()
    return questions


@connection.connection_handler
def save_user(cursor, username, hashed_pw):
    try:
        cursor.execute("""
                        INSERT INTO users (username, password, registration_time, reputation)
                        VALUES (%(username)s, %(hashed_pw)s, CURRENT_TIMESTAMP, 0)
                        """, {'username': username, 'hashed_pw': hashed_pw})
    except psycopg2.errors.UniqueViolation:
        return "This username is already used. Please, try another!"


@connection.connection_handler
def get_hash_by_username(cursor, username):
    cursor.execute("""
                        SELECT password FROM users
                        WHERE username = %(username)s;
                    """, {'username': username})
    pw_hash = cursor.fetchone()
    return pw_hash['password'] if pw_hash else None


@connection.connection_handler
def get_user_id_by_username(cursor, username):
    cursor.execute("""
                        SELECT id FROM users
                        WHERE username = %(username)s;
                    """, {'username': username})
    user_id = cursor.fetchone()
    return user_id['id']


@connection.connection_handler
def get_question_user_id_by_question_id(cursor, question_id):
    cursor.execute("""
                        SELECT user_id FROM question
                        WHERE id = %(question_id)s;
                    """, {'question_id': question_id})
    user_id = cursor.fetchone()
    return user_id['user_id'] if user_id else None


@connection.connection_handler
def get_user_id_by_answer_id(cursor, answer_id):
    cursor.execute("""
                    SELECT user_id FROM answer
                    WHERE id = %(answer_id)s;
                    """, {'answer_id': answer_id})
    user_id = cursor.fetchone()
    return user_id['user_id'] if user_id else None


@connection.connection_handler
def get_user_id_by_comment_id(cursor, comment_id):
    cursor.execute("""
                    SELECT user_id FROM comment
                    WHERE id = %(comment_id)s;
                    """, {'comment_id': comment_id})
    user_id = cursor.fetchone()
    return user_id['user_id'] if user_id else None


@connection.connection_handler
def update_user_reputation(cursor, user_id, value):
    cursor.execute("""
                    update users
                    set reputation = reputation + %(value)s
                    WHERE id = %(user_id)s;
    """, {'user_id': user_id,
          'value': value})

@connection.connection_handler
def accept_answer(cursor, answer_id):
    cursor.execute("""
                UPDATE answer
                SET accepted = true
                WHERE id = %(answer_id)s;
    """, {'answer_id': answer_id})


@connection.connection_handler
def get_users(cursor):
    cursor.execute("""
                    SELECT * FROM users;
                    """)
    return cursor.fetchall()


@connection.connection_handler
def update_view(cursor, question_id):
    cursor.execute("""
                UPDATE question
                SET view_number =  view_number + 1
                WHERE id = %(question_id)s;
                    """,
               {'question_id': question_id})