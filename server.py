from flask import Flask, render_template, request, redirect, url_for
import data_manager

app = Flask(__name__)



@app.route('/list')
def route_list():
    questions = data_manager.get_questions()
    return render_template('list.html', questions=questions)





if __name__ == '__main__':
    app.run(
        debug = True,
        port = 5000
    )