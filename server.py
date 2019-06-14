import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import data_manager
import util

UPLOAD_FOLDER = './static/images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/doG'


@app.route('/')
def route_index_page():
    questions = data_manager.get_latest_five_questions()
    type = 'list_five'
    return render_template('list.html', questions=questions, type=type)


@app.route('/list', methods=['GET', 'POST'])
def route_list():
    questions = data_manager.get_questions()
    type = 'list_all'
    if request.method == 'POST':
        search = request.form['search']
        search_results = data_manager.get_question_by_search(search)
        return render_template('search_result.html', search=search, results=search_results, questions=questions)
    return render_template('list.html', questions=questions, type=type)


@app.route('/list?order_by=<order_key>&order_direction=<order_direction>')
def route_list_ordered(order_key, order_direction):
    questions = data_manager.get_questions()
    return render_template('list.html', questions=questions, order_key=order_key, order_direction=order_direction)


@app.route('/question/<question_id>')
def route_question(question_id):
    question = data_manager.get_question_by_id(question_id)
    if question is None:
        error = f'There is no question with question_id {question_id}.'
        return render_template('error.html', error=error)

    data_manager.update_view(question_id)
    answers = data_manager.get_answers_with_comments_by_question_id(question_id)
    question_comments = data_manager.get_comments_from_question_id(question_id)
    return render_template('question.html', question=question, answers=answers, question_comments=question_comments)


@app.route('/add-question', methods=['GET', 'POST'])
@util.login_required
def add_question():
    if request.method == 'POST':
        user_id = data_manager.get_user_id_by_username(session['username'])
        new_question = dict(request.form)
        file_to_upload = request.files['image_file']
        new_question['image'] = save_file(file_to_upload)
        data_manager.add_question(new_question, user_id)
        return redirect('/list')
    questions = data_manager.get_questions()
    return render_template('add-question.html', questions=questions)


def save_file(file_to_upload):
    if not file_to_upload:
        return ''
    filename = secure_filename(file_to_upload.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_to_upload.save(filepath)
    return str(filepath)[1:]


@app.route('/question/<question_id>/delete', methods=['GET'])
@util.login_required
def delete_question(question_id):
    question_user_id = data_manager.get_question_user_id_by_question_id(question_id)
    if session['user_id'] == question_user_id:
        data_manager.delete_question_and_answers_by_id(question_id)
        return redirect('/list')
    else:
        return "You don't have the permission to delete this question!"


@app.route('/answer/<answer_id>/delete', methods=['GET'])
@util.login_required
def delete_answer(answer_id):
    answer_user_id = data_manager.get_user_id_by_answer_id(answer_id)
    if session['user_id'] == answer_user_id:
        question_id = data_manager.get_question_id_by_answer_id(answer_id)
        data_manager.delete_answer_with_image_by_id(answer_id)
        return redirect(url_for('route_question', question_id=question_id))
    else:
        return "You don't have the permission to delete this answer!"


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
@util.login_required
def new_answer(question_id):
    if request.method == 'POST':
        user_id = data_manager.get_user_id_by_username(session['username'])
        file_to_upload = request.files['image_file']
        answer_to_add = dict(request.form)
        answer_to_add['image'] = save_file(file_to_upload)
        data_manager.add_answer(answer_to_add, user_id)
        question_id = request.form['question_id']
        return redirect(url_for('route_question', question_id=question_id))
    question = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_answers_by_question_id(question_id)
    return render_template('new-answer.html', question=question, answers=answers)


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
@util.login_required
def edit_question(question_id):
    question_user_id = data_manager.get_question_user_id_by_question_id(question_id)
    if session['user_id'] != question_user_id:
        return "You don't have the permission to edit this question!"
    if request.method == 'POST':
        edited_question = dict(request.form)
        new_image = save_file(request.files['image_file'])
        edited_question['image'] = new_image
        edited_question['id'] = question_id
        data_manager.edit_question(edited_question)
        return redirect(url_for('route_question', question_id=question_id))
    question = data_manager.get_question_by_id(question_id)
    return render_template('edit.html', question=question)


@app.route('/question/<question_id>/<vote>')
def vote_question(question_id, vote):
    rep_num = 5 if vote == 'vote-up' else -2
    util.update_reputation('question', question_id, rep_num)
    data_manager.vote_question(question_id, vote)
    return redirect(url_for('route_question', question_id=question_id))


@app.route('/answer/<answer_id>/<vote>')
def vote_answer(answer_id, vote):
    rep_num = 10 if vote == 'vote-up' else -2
    util.update_reputation('answer', answer_id, rep_num)
    data_manager.vote_answer(answer_id, vote)
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    return redirect(url_for('route_question', question_id=question_id))


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
@util.login_required
def edit_answer(answer_id):
    answer_user_id = data_manager.get_user_id_by_answer_id(answer_id)
    if session['user_id'] == answer_user_id:
        if request.method == 'POST':
            edited_answer = dict(request.form)
            new_image = save_file(request.files['image_file'])
            edited_answer['image'] = new_image
            edited_answer['id'] = answer_id
            data_manager.edit_answer(edited_answer)

            question_id = data_manager.get_question_id_by_answer_id(answer_id)
            return redirect(url_for('route_question', question_id=question_id))
        question = data_manager.get_question_by_answer_id(answer_id)
        answer_to_edit = data_manager.get_answer_by_answer_id(answer_id)
        return render_template('edit.html', answer_to_edit=answer_to_edit, question=question)
    else:
        return "You don't have permission to edit this answer"


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
@util.login_required
def add_comment_to_question(question_id):
    if request.method == 'POST':
        user_id = data_manager.get_user_id_by_username(session['username'])
        data_manager.add_comment_to_question(question_id, dict(request.form), user_id)
        question_comments = data_manager.get_comments_from_question_id(question_id)
        return redirect(url_for('route_question', question_id=question_id, question_comments=question_comments))
    question = data_manager.get_question_by_id(question_id)
    return render_template('add-comment.html', question=question)


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
@util.login_required
def add_comment_to_answer(answer_id):
    if request.method == 'POST':
        user_id = data_manager.get_user_id_by_username(session['username'])
        comment_message = request.form['message']
        data_manager.add_comment_to_answer(answer_id, comment_message, user_id)
        question_id = data_manager.get_question_id_by_answer_id(answer_id)
        return redirect(url_for('route_question', question_id=question_id))
    question = data_manager.get_question_by_answer_id(answer_id)
    answer = data_manager.get_answer_by_answer_id(answer_id)
    return render_template('add-comment-to-answer.html', question=question, answer=answer)


@app.route('/comments/<comment_id>/edit', methods=['GET', 'POST'])
@util.login_required
def edit_comment(comment_id):
    comment_user_id = data_manager.get_user_id_by_comment_id(comment_id)
    if session.get('user_id') == comment_user_id:
        if request.method == 'POST':
            new_message = request.form['message']
            new_edited_count = int(request.form['edited_count']) + 1
            data_manager.edit_comment(comment_id, new_message, new_edited_count)
            question_id = data_manager.get_question_id_by_comment_id(comment_id)
            return redirect(url_for('route_question', question_id=question_id))
        comment = data_manager.get_comment_by_id(comment_id)
        return render_template('edit-comment.html', comment=comment)
    else:
        return "You don't have permission to edit this comment!"


@app.route('/comments/<comment_id>/delete')
@util.login_required
def delete_comment(comment_id):
    comment_user_id = data_manager.get_user_id_by_comment_id(comment_id)
    if session.get('user_id') == comment_user_id:
        question_id = data_manager.get_question_id_by_comment_id(comment_id)
        data_manager.delete_comment_by_id(comment_id)
        return redirect(url_for('route_question', question_id=question_id))
    else:
        return "You don't have the permission to delete this comment!"


@app.route('/users')
def list_users():
    users = data_manager.get_users()
    return render_template('list_users.html', users=users)


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        hashed_pw = util.hash_password(request.form['password'])
        user_name = request.form['username']
        error = data_manager.save_user(user_name, hashed_pw)
        if error:
            return render_template('reg_login.html',
                                   error=error,
                                   title='Registration',
                                   server_function='registration',
                                   submit_text='Register!')
        else:
            return redirect('/')
    return render_template('reg_login.html', title='Registration', server_function='registration', submit_text='Register!')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        hash = data_manager.get_hash_by_username(request.form['username'])
        if hash and util.verify_password(request.form['password'], hash):
            session['username'] = request.form['username']
            session['user_id'] = data_manager.get_user_id_by_username(session['username'])
            return redirect(url_for('route_list'))
        else:
            return render_template('reg_login.html',
                                   error='Wrong username/password',
                                   title='Login',
                                   server_function='login',
                                   submit_text='Login!')
    return render_template('reg_login.html', title='Login', server_function='login', submit_text='Login!')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('route_list'))


@app.route('/answer/<answer_id>/accept')
def accept_answer(answer_id):
    rep_num = 15
    util.update_reputation('answer', answer_id, rep_num)
    data_manager.accept_answer(answer_id)
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    return redirect(url_for('route_question', question_id=question_id))


if __name__ == '__main__':
    app.run(
        debug=True,
        port=5000
    )
