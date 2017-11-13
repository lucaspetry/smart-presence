from flask import Flask, render_template, request, redirect, url_for
from flask_restful import Resource, Api
from flask_jsonpify import jsonify
from base64 import b64encode, b64decode
from Crypto.PublicKey import RSA
from smart_presence import SmartPresence

app = Flask(__name__)
api = Api(app)

class Transaction(Resource):

    def post(self):
        block = {
            'id' : request.json['id'],
            'entity_pbk' : request.json['entity_pbk'],
            'authority_pbk' : request.json['authority_pbk'],
            'timestamp' : request.json['timestamp'],
            'entity_lat' : request.json['entity_lat'],
            'entity_lon' : request.json['entity_lon'],
            'entity_signature' : request.json['entity_signature'],
            'authority_signature' : request.json['authority_signature']
        }

        sp = SmartPresence.fromJSON(block)

        # TO-DO process transaction sp

        return {'status' : 'success'}

api.add_resource(Transaction, '/transaction')