import json
import random
import Crypto.Hash.SHA256 as SHA256
from base64 import b64encode, b64decode
from smart_presence import SmartPresence
import time, calendar
from Crypto.PublicKey import RSA

# A block chain
class Blockchain(object):

	# Constructs a block chain with blocks holding <block_size> transactions each
	def __init__(self, block_size=5):
		self.block_size = block_size
		self.blocks = []
		self.pending_transactions = []

	# True if the given <block> is within the chain, False otherwise
	def contains_block(self, block):
		for b in blocks:
			if b.hash == block.hash:
				return True

		return False

	# Returns the last block of the chain
	def get_last_block(self):
		if self.length() > 0:
			return self.blocks[-1]
		else:
			return None

	# Returns the latest <count> blocks of the chain
	def get_last_blocks(self, count):
		return self.blocks[-count:]

	# Returns the block for the given <id>
	def get_block(self, id):
		for block in self.blocks:
			if block.id == id:
				return block

		return None

	# Adds a single block to the chain only if the block is valid
	def add_block(self, block, authorities):
		if block.is_valid(authorities):
			self.blocks.append(block)
			return True
		
		return False

	# Returns the length of the chain
	def length(self):
		return len(self.blocks)

	# True if the entire chain is valid, False otherwise
	def is_valid(self, authorities):
		for block in self.blocks:
			if not block.is_valid(authorities):
				return False

		return True

	# Returns the json file representing the chain
	def json(self):
		return [block.json() for block in self.blocks]

# A block of transactions
class Block(object):

	# Creates a block from its json file
	@staticmethod
	def fromJSON(json):
		public_key = RSA.importKey(b64decode(json['public_key']))

		obj = Block(public_key, [], None)
		obj.id = json['id']
		obj.timestamp = time.gmtime(calendar.timegm(json['timestamp']))
		obj.parent_hash = b64decode(json['parent_hash']) if json['parent_hash'] else None
		obj.size = json['transaction_count']
		obj.transactions = [SmartPresence.fromJSON(t) for t in json['transactions']]
		obj.hash = b64decode(json['hash'])
		obj.signature = b64decode(json['signature'])

		return obj

	# Constructs a block that holds <transactions>, preceded by <parent>
	def __init__(self, public_key, transactions, parent=None):
		self.id = parent.id + 1 if parent else 1
		self.timestamp = time.gmtime()
		self.public_key = public_key
		self.transactions = transactions
		self.parent = parent
		self.parent_hash = self.parent.hash if self.parent else ''
		self.size = len(transactions)
		self.hash = self.to_SHA256()
		self.signature = None

	# Signs the block with the given authority <key_pair>
	def sign(self, key_pair):
		self.signature = key_pair.decrypt(self.to_SHA256())

	# True if the block is valid, False otherwise
	def is_valid(self, authorities):
		# Block ID is greater than parent ID by 1
		if self.parent and self.id - self.parent.id != 1:
			return False

		# Stored parent hash is equals to actual parent hash
		if self.parent and self.parent.hash != self.parent_hash:
			return False

		# Timestamp of block creation is higher than parent's timestamp
		if self.parent and self.timestamp < self.parent.timestamp:
			return False

		# Stored hash is equals to generated block hash
		if self.hash != self.to_SHA256():
			return False

		# All transactions are valid
		for transaction in self.transactions:
			if not transaction.is_valid(authorities):
				return False

		return self.check_signature(authorities)

	# True if the signature is valid, False otherwise
	def check_signature(self, authorities):
		if not self.public_key:
			print('Check signature: public key missing.')
			return False

		if not self.signature:
			print('Check signature: signature missing.')
			return False

		found = False
		for authority in authorities.values():
			if authority['public_key'] == str(b64encode(self.public_key.exportKey()).decode('utf-8')):
				found = True
				break

		if not found:
			print('Check signature: unauthorized public key.')
			return False

		hash = self.to_SHA256()
		generatedHash = self.public_key.encrypt(self.signature, '')[0]

		if hash != generatedHash:
			print('Check signature: signature is invalid.')
			return False

		return True

	# Returns the SHA256 digest of the block
	def to_SHA256(self):
		return SHA256.new(self.to_base64()).digest()

	# Returns the base64 representation of the block
	def to_base64(self):
		parent_hash = None

		if self.parent:
			parent_hash = b64encode(self.parent_hash).decode('utf-8')

		block_content = {
			'id': self.id,
			'public_key' : str(b64encode(self.public_key.exportKey()).decode('utf-8')),
			'timestamp' : self.timestamp,
			'parent_hash': parent_hash, 
			'transaction_count': self.size, 
			'transactions': [t.json() for t in self.transactions]
		}

		return b64encode(bytes(json.dumps(block_content, sort_keys=True), 'utf-8'))

	# Returns the json file representing the block
	def json(self):
		parent_hash = None

		if self.parent:
			parent_hash = b64encode(self.parent_hash).decode('utf-8')

		json_block = {
			'id': self.id,
			'public_key' : str(b64encode(self.public_key.exportKey()).decode('utf-8')),
			'timestamp' : self.timestamp,
			'parent_hash': parent_hash,
			'transaction_count': self.size,
			'transactions': [t.json() for t in self.transactions],
			'hash': b64encode(self.hash).decode('utf-8'),
			'signature': b64encode(self.signature).decode('utf-8')
		}

		return json_block
