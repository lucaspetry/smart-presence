from flask import Flask, render_template, request, redirect, url_for
from flask_restful import Resource, Api
from flask_jsonpify import jsonify
from Crypto.PublicKey import RSA
from smart_presence import SmartPresence
from blockchain import Blockchain, Block
import sys
from base64 import b64encode, b64decode
import json

app = Flask(__name__)
api = Api(app)

PORT = sys.argv[1]

authorities = {}
settings = {}

with open('app/network_setup.json') as network_setup_file:
    data = json.load(network_setup_file)
    authorities = data['authorities']
    settings = data['network']

##########################################################
# Network Info
##########################################################
BLOCK_SIZE = settings['block_size']
BLOCK_PERIOD = settings['block_period'] # Seconds
AUTHORITY_COUNT = settings['authority_count']
OUT_OF_TURN_DELAY = settings['out_of_turn_delay'] * AUTHORITY_COUNT # Seconds

##########################################################
# Authority Info
##########################################################
AUTHORITY_NAME = authorities[str(PORT)]['name']
AUTHORITY_KEYPAIR = RSA.importKey(b64decode(authorities[str(PORT)]['key_pair']))
AUTHORITY_PBK = AUTHORITY_KEYPAIR.publickey()

chain = Blockchain(BLOCK_SIZE)
pending_transactions = []

class TransactionAppRes(Resource):

    def post(self):
        transaction = {
            'id' : request.json['id'],
            'entity_pbk' : request.json['entity_pbk'],
            'authority_pbk' : request.json['authority_pbk'],
            'timestamp' : request.json['timestamp'],
            'entity_lat' : request.json['entity_lat'],
            'entity_lon' : request.json['entity_lon'],
            'entity_signature' : request.json['entity_signature'],
            'authority_signature' : request.json['authority_signature']
        }

        self.process_transaction(transaction)
        return {'status' : 'success'}

    def process_transaction(self, transaction):
        global pending_transactions, chain
        sp = SmartPresence.fromJSON(transaction)
        pending_transactions.append(sp)

        if len(pending_transactions) == BLOCK_SIZE:
            block = Block(AUTHORITY_PBK, pending_transactions, chain.get_last_block())
            block.sign(AUTHORITY_KEYPAIR)

            if chain.add_block(block, authorities):
                print("Blockchain: block added!")
                # Propagate block to other nodes
                # Wait for confirmation (callback)

                pending_transactions = []
            else:
                print('Blockchain: block refused! One or more transactions are invalid.')
                # Do something to fix the block, 
                # maybe by ditching any invalid transactions
                # and adding the remainder to the pending_transactions list
                remainder_transactions = []
                for transaction in pending_transactions:
                    if transaction.is_valid(authorities):
                        remainder_transactions.append(transaction)

                pending_transactions = remainder_transactions

class BlockRes(Resource):

    def post(self):
        block = Block.fromJSON(request.json['block'])

        if chain.contains_block(block):
            return {'status' : 'failure'}

        if chain.add_block(block, authorities):
            return {'status' : 'success'}

        return {'status' : 'failure'}

class BlockGetRes(Resource):

    def get(self, id):
        block = chain.get_block(id)
        block = block.json() if block else {}
        return jsonify(block)

class BlocksRes(Resource):

    def get(self, count):
        return jsonify(sorted([b.json() for b in chain.get_last_blocks(count)], \
            key=lambda block: block['id'], reverse=True))

api.add_resource(TransactionAppRes, '/transaction')
api.add_resource(BlockRes, '/block')
api.add_resource(BlockGetRes, '/block/<int:id>')
api.add_resource(BlocksRes, '/blocks/<int:count>')

app.run(port=PORT)