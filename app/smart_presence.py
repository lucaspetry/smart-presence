import time, calendar
import Crypto.Hash.SHA256 as SHA256
import Crypto.PublicKey.RSA as RSA
from base64 import b64encode, b64decode 
from json import load 

class SmartPresence(object):

	@staticmethod
	def fromJSON(json):
		authorityKey = RSA.importKey(b64decode(json['authority_pbk']))
		entityKey = RSA.importKey(b64decode(json['entity_pbk']))

		obj = SmartPresence(json['id'], authorityKey, entityKey, json['entity_lat'], json['entity_lon'])
		obj.timestamp = time.gmtime(calendar.timegm(json['timestamp']))
		obj.entity_signature = b64decode(json['entity_signature'][2:-1])
		obj.authority_signature = b64decode(json['authority_signature'][2:-1])
		obj.pending = None
		obj.approved = None

		return obj

	def __init__(self, id, authority_pbk, entity_pbk, entity_lat, entity_lon):
		self.id = id
		self.authority_pbk = authority_pbk
		self.entity_pbk = entity_pbk
		self.timestamp = time.gmtime()
		self.entity_lat = entity_lat
		self.entity_lon = entity_lon
		self.entity_signature = None
		self.authority_signature = None
		self.pending = True
		self.approved = None

	def is_valid(self):
		with open('app/authorities.json') as authorities_file:
			data = load(authorities_file)
			authorities = data['authorities']

			found = False
			for authority in authorities:
				if authority['public_key'] == str(b64encode(self.authority_pbk.exportKey()).decode('utf-8')):
					found = True
					break

			# if not found:
			# 	return False

		return self.check_signatures() # What else?

	def sign_entity(self, entity_key_pair):
		self.entity_signature = entity_key_pair.decrypt(self.to_SHA256())

	def sign_authority(self, authority_key_pair):
		self.authority_signature = authority_key_pair.decrypt(self.to_SHA256())

	def check_signatures(self):
		if not self.authority_pbk or not self.entity_pbk:
			print('Check signatures: public key missing.')
			return False

		if not self.authority_signature or not self.entity_signature:
			print('Check signatures: signature missing.')
			return False

		hash = self.to_SHA256() # Should look up public keys externally
		hashAuthority = self.authority_pbk.encrypt(self.authority_signature, '')[0]
		hashEntity = self.entity_pbk.encrypt(self.entity_signature, '')[0]

		if hash != hashAuthority:
			print('Check signatures: authority signature is invalid.')
			return False

		if hash != hashEntity:
			print('Check signatures: entity signature is invalid.')
			return False

		return True

	def to_SHA256(self):
		return SHA256.new(self.to_base64()).digest()

	def to_base64(self):
		string = str(self.timestamp) + str(self.authority_pbk.exportKey()) + str(self.entity_pbk.exportKey()) \
		+ str(self.entity_lat) + str(self.entity_lon)

		return b64encode(bytes(string, 'utf-8'))

	def json(self):
		block = {
			'id' : self.id,
			'entity_pbk' : str(b64encode(self.entity_pbk.exportKey()).decode('utf-8')),
			'authority_pbk' : str(b64encode(self.authority_pbk.exportKey()).decode('utf-8')),
			'timestamp' : self.timestamp,
			'entity_lat' : self.entity_lat,
			'entity_lon' : self.entity_lon,
			'entity_signature' : str(b64encode(self.entity_signature)),
			'authority_signature' : str(b64encode(self.authority_signature))
		}

		return block