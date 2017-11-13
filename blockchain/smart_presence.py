import time, calendar
import Crypto.Hash.SHA256 as SHA256
import Crypto.PublicKey.RSA as RSA
from base64 import b64encode, b64decode 

class SmartPresence(object):

	@staticmethod
	def fromJSON(json):
		obj = SmartPresence(json['id'], RSA.importKey(b64decode(json['authority_pbk'][2:-1])), \
			RSA.importKey(b64decode(json['entity_pbk'][2:-1])), json['entity_lat'], json['entity_lon'])

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
		print(self.to_base64())
		return SHA256.new(self.to_base64()).digest()

	def to_base64(self):
		string = str(self.timestamp) + str(self.authority_pbk) + str(self.entity_pbk) \
		+ str(self.entity_lat) + str(self.entity_lon)

		return b64encode(bytes(string, 'utf-8'))

	def json(self):
		block = {
			'id' : self.id,
			'entity_pbk' : str(b64encode(self.entity_pbk.exportKey())),
			'authority_pbk' : str(b64encode(self.authority_pbk.exportKey())),
			'timestamp' : self.timestamp,
			'entity_lat' : self.entity_lat,
			'entity_lon' : self.entity_lon,
			'entity_signature' : str(b64encode(self.entity_signature)),
			'authority_signature' : str(b64encode(self.authority_signature))
		}

		return block