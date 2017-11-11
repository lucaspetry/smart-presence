from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/view-blocks')
def view_blocks():
    return render_template('view-blocks.html')

@app.route('/new-session')
def new_session():
    return render_template('new-session.html')

@app.route('/create-session')
def create_session():
    assert request.method == 'POST'
    return render_template('view-session.html', id=68687)

@app.route('/view-session/<int:id>')
def view_session(id):
    return render_template('view-session.html', id=id)

@app.route('/register-presence/', methods=['GET', 'POST'])
def register_presence():
    if request.method == 'POST':
        return render_template('register-presence.html', id=request.form['session-id'])

    return render_template('register-presence.html', id=None)

@app.route('/user/<string:username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username