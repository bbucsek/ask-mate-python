from datetime import datetime
import data_manager
from time import time
import bcrypt
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, escape


def str_timestamp_to_datetime(timestamp_text):
    """Converts string containing UNIX timestamp to datetime object"""
    return datetime.fromtimestamp(int(timestamp_text))


def new_id():
    questions = data_manager.get_questions()
    current_id = 0
    for question in questions:
        if int(question['id']) > current_id:
            current_id = int(question['id'])
    return current_id + 1


def get_current_timestamp():
    return int(time())


def hash_password(plain_text_password):
    # By using bcrypt, the salt is saved into the hash itself
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hash_to_verify):
    hashed_bytes_password = hash_to_verify.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('username'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def update_reputation(table_name, id, rep_num):
    if table_name == 'question':
        user_id = data_manager.get_question_user_id_by_question_id(id)
        data_manager.update_user_reputation(user_id, rep_num)
    else:
        user_id = data_manager.get_user_id_by_answer_id(id)
        data_manager.update_user_reputation(user_id, rep_num)
