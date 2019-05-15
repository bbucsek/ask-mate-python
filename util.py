from datetime import datetime
import data_manager
from time import time



def str_timestamp_to_datetime(timestamp_text):
    """Converts string containing UNIX timestamp to datetime object"""
    return datetime.fromtimestamp(int(timestamp_text))


def new_id():
    questions = data_manager.get_questions()
    current_id = 0
    for question in questions:
        if question['id'] > current_id:
            current_id = question['id']
    return int(current_id) + 1

def get_current_timestamp():
    return int(time())
