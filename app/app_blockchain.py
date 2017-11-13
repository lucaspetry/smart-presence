from flask import Flask, render_template, request, redirect, url_for
from flask_restful import Resource, Api
from flask_jsonpify import jsonify
from Crypto.PublicKey import RSA
from smart_presence import SmartPresence
from blockchain import Blockchain, Block

app = Flask(__name__)
api = Api(app)

BLOCK_SIZE = 5

chain = Blockchain(BLOCK_SIZE)
pending_transactions = []

class TransactionRes(Resource):

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

        sp = SmartPresence.fromJSON(transaction)
        pending_transactions.append(sp)

        if len(pending_transactions) == BLOCK_SIZE:
            block = Block(pending_transactions, chain.last_block())
            chain.add_block(block)

            # Propagate block to other nodes
            # Wait for confirmation (callback)

            pending_transactions.clear()

        return {'status' : 'success'}

class BlockRes(Resource):

    def post(self):
        block = None # Block() # TO-DO materialize block

        if chain.contains_block(block):
            return {'status' : 'failure'}

        if chain.add_block(block):
            return {'status' : 'success'}

        return {'status' : 'failure'}

class BlocksRes(Resource):

    def get(self, count):
        return [b.json() for b in chain.get_last_blocks(count)]


api.add_resource(TransactionRes, '/transaction')
api.add_resource(BlockRes, '/block')
api.add_resource(BlocksRes, '/blocks/<int:count>')