import connection
import util

QUESTIONS_FILENAME = 'question.csv'
QUESTIONS_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWERS_FILENAME = 'answer.csv'
ANSWERS_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def get_questions():
    detailed_questions = connection.read_csv('question.csv')
    questions = []
    for question in detailed_questions:
        new_question = {'id': question.get('id'),
                        'submission_time': util.str_timestamp_to_datetime(question.get('submission_time')),
                        'title': question.get('title')}
        questions.append(new_question)
    return questions


def get_answers_by_question_id(question_id):
    all_answers = connection.read_csv('answer.csv')
    answers_for_question = []
    for answer in all_answers:
        if answer['question_id'] == question_id:
            answer['submission_time'] = util.str_timestamp_to_datetime(answer['submission_time'])
            answers_for_question.append(answer)
    return answers_for_question


def get_question_by_id(question_id):
    all_questions = connection.read_csv('question.csv')
    for question in all_questions:
        if question['id'] == question_id:
            question['submission_time'] = util.str_timestamp_to_datetime(question['submission_time'])
            return question


def add_question(user_question):
    questions = connection.read_csv(QUESTIONS_FILENAME)

    new_question = init_question()
    # fields from user
    new_question['title'] = user_question['title']
    new_question['message'] = user_question['message']
    new_question['image'] = None
    questions.append(new_question)

    connection.write_csv(questions, QUESTIONS_FILENAME, QUESTIONS_HEADER)


def init_question():
    """Initial values for id, submission_time, view_number, vote_number"""
    question = {}
    question['id'] = util.new_id()
    question['submission_time'] = util.get_current_timestamp()
    question['view_number'] = 0
    question['vote_number'] = 0
    return question


def delete_question_and_answers_by_id(quxestion_id):
    questions = connection.read_csv(QUESTIONS_FILENAME)
    all_answers = connection.read_csv(ANSWERS_FILENAME)
    for question in questions:
        if question['id'] == question_id:
            del question
            break

    for answer in list(all_answers):
        if answer['question_id'] == question_id:
            all_answers.remove(answer)

    connection.write_csv(questions, QUESTIONS_FILENAME, QUESTIONS_HEADER)
    connection.write_csv(all_answers, ANSWERS_FILENAME, ANSWERS_HEADER)


