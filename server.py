import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import data_manager

UPLOAD_FOLDER = './static/images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
@app.route('/list')
def route_list():
    questions = data_manager.get_questions()
    return render_template('list.html', questions=questions)


@app.route('/list?order_by=<order_key>&order_direction=<order_direction>')
def route_list_ordered(order_key, order_direction):
    questions = data_manager.get_questions()
    return render_template('list.html', questions=questions, order_key=order_key, order_direction=order_direction)


@app.route('/question/<question_id>')
def route_question(question_id):
    question = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_answers_by_question_id(question_id)
    return render_template('question.html', question=question, answers=answers)


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        new_question = dict(request.form)
        file_to_upload = request.files['image_file']
        new_question['image'] = save_file(file_to_upload)
        data_manager.add_question(new_question)
        return redirect('/list')
    questions = data_manager.get_questions()
    return render_template('/add-question.html', questions=questions)


def save_file(file_to_upload):
    if not file_to_upload:
        return ''
    filename = secure_filename(file_to_upload.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_to_upload.save(filepath)
    return str(filepath)[1:]


@app.route('/question/<question_id>/delete', methods=['POST'])
def delete_question(question_id):
    if request.method == 'POST':
        data_manager.delete_question_and_answers_by_id(question_id)
        return redirect('/list')


@app.route('/answer/<answer_id>/delete', methods=['POST'])
def delete_answer(answer_id):
    if request.method == 'POST':
        data_manager.delete_answer_by_id(answer_id)
        question_id = request.form['question_id']
        return redirect(url_for('route_question', question_id=question_id))


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def new_answer(question_id):
    if request.method == 'POST':
        file_to_upload = request.files['image_file']
        answer_to_add = dict(request.form)
        answer_to_add['image'] = save_file(file_to_upload)
        data_manager.add_answer(answer_to_add)
        question_id = request.form['question_id']
        return redirect(url_for('route_question', question_id=question_id))
    question = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_answers_by_question_id(question_id)
    return render_template('/new-answer.html', question=question, answers=answers)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit_question(question_id):
    if request.method == 'POST':
        question_id = request.form['id']
        data_manager.edit_question(question_id, dict(request.form))
        return redirect(url_for('route_question', question_id=question_id))
    question = data_manager.get_question_by_id(question_id)
    return render_template('/edit.html', question_id=question_id, question=question)


@app.route('/question/<question_id>/<vote>')
def vote_question(question_id, vote):
    data_manager.vote_question(question_id, vote)
    return redirect(url_for('route_question', question_id=question_id))


@app.route('/answer/<answer_id>/<vote>')
def vote_answer(answer_id, vote):
    question_id = data_manager.get_question_id_from_answer_id(answer_id)
    data_manager.vote_answer(answer_id, vote)
    question = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_answers_by_question_id(question_id)
    return render_template('question.html', question=question, answers=answers)


if __name__ == '__main__':
    app.run(
        debug=True,
        port=5000
    )
