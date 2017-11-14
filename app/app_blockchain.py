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
BLOCK_SIZE = 1

authorities = {}

with open('app/authorities.json') as authorities_file:
    authorities = json.load(authorities_file)['authorities']

AUTHORITY_NAME = authorities[str(PORT)]['name']
AUTHORITY_KEYPAIR = RSA.importKey(b64decode(authorities[str(PORT)]['key_pair']))
AUTHORITY_PBK = AUTHORITY_KEYPAIR.publickey()

chain = Blockchain(BLOCK_SIZE)
pending_transactions = []

class TransactionRes(Resource):

    def post(self):
        global pending_transactions, chain

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

        sp = SmartPresence.fromJSON(transaction)
        pending_transactions.append(sp)

        if len(pending_transactions) == BLOCK_SIZE:
            block = Block(pending_transactions, chain.get_last_block())
            ret = chain.add_block(block)
            if ret:
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
                    if transaction.is_valid():
                        remainder_transactions.append(transaction)

                pending_transactions = remainder_transactions


        return {'status' : 'success'}

class BlockRes(Resource):

    def post(self):
        block = Block.fromJSON(request.json['block'])

        if chain.contains_block(block):
            return {'status' : 'failure'}

        if chain.add_block(block):
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

api.add_resource(TransactionRes, '/transaction')
api.add_resource(BlockRes, '/block')
api.add_resource(BlockGetRes, '/block/<int:id>')
api.add_resource(BlocksRes, '/blocks/<int:count>')

app.run(port=PORT)