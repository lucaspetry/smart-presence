from flask import Flask, render_template, request, redirect, url_for
from session import Session
from smart_presence import SmartPresence
from blockchain import Block
import random
from Crypto.PublicKey import RSA
import time
import requests
import json
from base64 import b64encode, b64decode
import sys

app = Flask(__name__)

PORT = sys.argv[1] # Port where application is running
PORT_NODE = 5002 # Port where corresponding authority is running
RAND_BITS = 20

authorities = {}

with open('app/network_setup.json') as authorities_file:
    authorities = json.load(authorities_file)['authorities']

##########################################################
# Authority Info
##########################################################
AUTHORITY_NAME = authorities[str(PORT_NODE)]['name']
AUTHORITY_KEYPAIR = RSA.importKey(b64decode(authorities[str(PORT_NODE)]['key_pair']))
AUTHORITY_PBK = AUTHORITY_KEYPAIR.publickey()

##########################################################
# Blockchain Node Info
##########################################################
BLOCK_COUNT = 10
URL_GET_BLOCKS = 'http://127.0.0.1:' + str(PORT_NODE) + '/blocks/' + str(BLOCK_COUNT)
URL_GET_BLOCK = 'http://127.0.0.1:' + str(PORT_NODE) + '/block/'
URL_POST_TRANSACTION = 'http://127.0.0.1:' + str(PORT_NODE) + '/transaction'

sessions = { 1 : Session(1, "Teste", AUTHORITY_PBK) }
presences = {}

def format_datetime(value):
    return time.strftime('%m/%d/%Y %H:%M:%S UTC', value)

def format_key(value):
    return str(value).replace("\\n", "")

def base64_encode(value):
    return b64encode(value).decode('utf-8') if value else 'null'

app.jinja_env.filters['format_datetime'] = format_datetime
app.jinja_env.filters['format_key'] = format_key
app.jinja_env.filters['base64_encode'] = base64_encode

def postTransaction(transaction):
    headers = {'content-type': 'application/json'}
    response = requests.post(URL_POST_TRANSACTION, data=json.dumps(transaction.json()), headers=headers)

def getBlocks():
    response = requests.get(URL_GET_BLOCKS)
    return [Block.fromJSON(block) for block in response.json()]

def getBlock(id):
    response = requests.get(URL_GET_BLOCK + str(id))
    return Block.fromJSON(response.json())

def createSession(name):
    id = random.getrandbits(RAND_BITS)

    while id in sessions:
        id = random.getrandbits(RAND_BITS)

    sessions[id] = Session(id, name, AUTHORITY_PBK)
    return sessions[id]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/view-blocks')
def view_blocks():
    print(getBlocks())
    return render_template('view-blocks.html', blocks=getBlocks())

@app.route('/view-block/<int:id>')
def view_block(id):
    print(getBlocks())
    return render_template('view-block.html', block=getBlock(id))

@app.route('/new-session')
def new_session():
    return render_template('new-session.html', authority_name=AUTHORITY_NAME, \
        authority_pbk=AUTHORITY_PBK)

@app.route('/create-session', methods=['POST'])
def create_session():
    assert request.method == 'POST'

    session = createSession(request.form['session-name'])
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
        privateKey = request.form.get('private-key', type=str)
        privateKey = bytes(privateKey, 'utf-8') if privateKey else None
        keyPair = RSA.importKey(privateKey) if privateKey else None
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)

        if keyPair:
            id = random.getrandbits(RAND_BITS)

            while id in presences:
                id = random.getrandbits(RAND_BITS)

            sp = SmartPresence(id, AUTHORITY_PBK, keyPair.publickey(), latitude, longitude)
            sp.sign_entity(keyPair)
            presences[id] = sp
            sessions[sessionId].pendingTransactions[sp.id] = sp

            return redirect(url_for('view_presence', sessionId=sessionId, presenceId=id))
        elif sessionId in sessions:
            return render_template('register-presence.html', session=sessions[sessionId], error=None)

        return render_template('register-presence.html', session=None, error='The requested session does not exist.')

    return render_template('register-presence.html', session=None, error=None)

@app.route('/process-presence/', methods=['POST'])
def process_presence():
    assert request.method == 'POST'

    status = request.form.get('status', type=str)
    sessionId = request.form.get('session-id', type=int)
    presenceId = request.form.get('presence-id', type=int)

    session = sessions[sessionId]
    presence = presences[presenceId]

    presence.pending = False
    presence.approved = True if status == 'approve' else False

    session.pendingTransactions.pop(presenceId)

    if presence.approved:
        presence.sign_authority(AUTHORITY_KEYPAIR)
        session.approvedTransactions[presenceId] = presence
        postTransaction(presence)
    else:
        session.rejectedTransactions[presenceId] = presence

    return redirect(url_for('view_session', id=sessionId))

@app.route('/view-presence/<int:sessionId>/<int:presenceId>')
def view_presence(sessionId, presenceId):
    if sessionId in sessions and presenceId in presences:
        return render_template('view-presence.html', session=sessions[sessionId], \
            presence=presences[presenceId], error=None)

    return render_template('view-presence.html', session=None, presence=None, \
        error='The requested session/presence does not exist.')

@app.route('/user/<string:username>')
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username

app.run(port=PORT)