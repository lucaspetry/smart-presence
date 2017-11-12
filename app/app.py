from flask import Flask, render_template, request, redirect, url_for
from session import Session
import random

app = Flask(__name__)

sessions = {}

RAND_BITS = 20

def createSession(name, publicKey):
    id = random.getrandbits(RAND_BITS)

    while id in sessions:
        id = random.getrandbits(RAND_BITS)

    sessions[id] = Session(id, name, publicKey)
    return sessions[id]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/view-blocks')
def view_blocks():
    return render_template('view-blocks.html')

@app.route('/new-session')
def new_session():
    return render_template('new-session.html')

@app.route('/create-session', methods=['POST'])
def create_session():
    assert request.method == 'POST'

    session = createSession(request.form['session-name'], request.form['public-key'])
    return redirect(url_for('view_session', id=session.id))

@app.route('/close-session', methods=['POST'])
def close_session():
    assert request.method == 'POST'

    id = request.form.get('id', type=int)

    if id in sessions:
        sessions[id].open = False

    return redirect(url_for('view_session', id=id))

@app.route('/view-session/<int:id>')
def view_session(id):
    if id in sessions:
        return render_template('view-session.html', session=sessions[id])

    return render_template('view-session.html', session=None)

@app.route('/register-presence/', methods=['GET', 'POST'])
def register_presence():
    if request.method == 'POST':
        sessionId = request.form.get('session-id', type=int)
        publicKey = request.form.get('public-key', type=str)
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)

        if publicKey != None:
            # TODO Presence registration
            
            return redirect(url_for('view_presence', sessionId=sessionId, userPK=publicKey))
        elif sessionId in sessions:
            return render_template('register-presence.html', session=sessions[sessionId], error=None)

        return render_template('register-presence.html', session=None, error='The requested session does not exist.')

    return render_template('register-presence.html', session=None, error=None)

@app.route('/view-presence/<int:sessionId>/<int:userPK>')
def view_presence(sessionId, userPK):
    # TODO
    return render_template('view-presence.html', transaction=None)

@app.route('/user/<string:username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username