import time
import Crypto.Hash.SHA256 as SHA256
import Crypto.PublicKey.RSA as RSA
from base64 import b64encode, b64decode 

class SmartPresence(object):

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
			return False

		if not self.authority_signature or not self.entity_signature:
			return False

		hash = self.to_SHA256() # Should look up public keys externally
		hashAuthority = self.authority_pbk.encrypt(self.authority_signature, '')[0]
		hashEntity = self.entity_pbk.encrypt(self.entity_signature, '')[0]
		return hash == hashAuthority and hash == hashEntity

	def to_SHA256(self):
		return SHA256.new(self.to_base64()).digest()

	def to_base64(self):
		string = str(self.timestamp) + str(self.authority_pbk) + str(self.entity_pbk) \
		+ str(self.entity_lat) + str(self.entity_lon)

		return b64encode(bytes(string, 'utf-8'))