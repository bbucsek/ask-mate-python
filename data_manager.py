import connection


def get_questions():
    detailed_questions = connection.read_csv('question.csv')
    questions = []
    for question in detailed_questions:
        new_question = {'id': question.get('id'),
                        'submission_time': question.get('submission_time'),
                        'title': question.get('title')}
        questions.append(new_question)
    return questions

