from datetime import datetime


def str_timestamp_to_datetime(timestamp_text):
    """Converts string containing UNIX timestamp to datetime object"""
    return datetime.fromtimestamp(int(timestamp_text))
