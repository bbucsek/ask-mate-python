import connection
from datetime import datetime


def get_questions():
    detailed_questions = connection.read_csv('question.csv')
    questions = []
    for question in detailed_questions:
        new_question = {'id': question.get('id'),
                        'submission_time': str_timestamp_to_datetime(question.get('submission_time')),
                        'title': question.get('title')}
        questions.append(new_question)
    return questions


def str_timestamp_to_datetime(timestamp_text):
    """Converts string containing UNIX timestamp to datetime object"""
    return datetime.fromtimestamp(int(timestamp_text))
