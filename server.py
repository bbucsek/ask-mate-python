from flask import Flask, render_template, request, redirect, url_for
import data_manager

app = Flask(__name__)


@app.route('/')
@app.route('/list')
def route_list():
    questions = data_manager.get_questions()
    return render_template('list.html', questions=questions)


@app.route('/question/<question_id>')
def route_question(question_id):
    question = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_answers_by_question_id(question_id)
    return render_template('question.html', question=question, answers=answers)


@app.route('/add-question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        data_manager.add_question(dict(request.form))
        return redirect('/list')
    return render_template('/add-question.html')


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
def new_answer():
    if request.method == 'POST':
        data.manager.add_answer(dict(request.form))
        return redirect('/list')
    return render_template('/new-answer.html')



if __name__ == '__main__':
    app.run(
        debug = True,
        port = 5000
    )