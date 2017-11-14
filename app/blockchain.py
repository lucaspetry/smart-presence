import json
import random
import Crypto.Hash.SHA256 as SHA256
from base64 import b64encode, b64decode
from smart_presence import SmartPresence
import time, calendar

class Blockchain(object):

	def __init__(self, block_size=5):
		self.block_size = block_size
		self.blocks = []
		self.pending_transactions = []

	def contains_block(self, block):
		for b in blocks:
			if b.hash == block.hash:
				return True

		return False

	def get_last_blocks(self, count):
		return self.blocks[-count:]

	def get_block(self, id):
		for block in self.blocks:
			if block.id == id:
				return block

		return None

	# Function to add a single block to the chain
	def add_block(self, block):
		if block.is_valid():
			self.blocks.append(block)
			return True
		
		return False

	# Function to add all transactions, creating the blocks inside the function
	# TODO see if there's any use for this function now, or if this is legacy code
	def add_transactions(self, transactions):
		# Add the pending transactions, if there are any
		transactions = self.pending_transactions + transactions

		# Every block other than the first must have always <max_block_size> transactions.
		if len(transactions) < self.max_block_size:
			return
		else:
			# Only add valid transactions
			while len(transactions) > 0:
				# Create a copy of the current state to work on
				# The current state will only be updated when the block is created
				# And guaranteed to be valid.
				state = self.accounts_state.copy()
				valid_transactions = []

				while len(transactions) > 0 and len(valid_transactions) < self.max_block_size:
					transaction = transactions.pop(0)
					if transaction.is_valid(state):
						valid_transactions.append(transaction)
						state = transaction.execute(state)

				# If the block hasn't reached it's max size, store the transactions to add on a later date.
				# (This would happen if the first condition in the inside loop is true, but the second is false)
				# If it has reached it's max size, create the block and add it to the chain, 
				# and continue adding other transactions, if there are any
				# (This would happen if the second condition in the inside loop is true)
				if len(valid_transactions) < self.max_block_size:
					self.pending_transactions = valid_transactions
					return
				else:
					parent = self.last_block()
					block = Block(valid_transactions, parent.id+1, parent)

					# Verify if the block is valid
					# TODO check if this is really necessary
					# after all the work done to make sure no invalid transactions are added
					if block.is_valid(self.accounts_state):
						self.blocks.append(block)
						self.accounts_state = block.get_final_state(self.accounts_state)


		# parent = self.last_block()
		# block = Block(transactions, parent.id+1, parent)

		# if block.is_valid(self.accounts_state):
		# 	self.blocks.append(block)
		# 	self.accounts_state = block.get_final_state(self.accounts_state)

	def length(self):
		return len(self.blocks)

	def last_block(self):
		if self.length() > 0:
			return self.blocks[-1]
		else:
			# Show error or something
			return

	# The chain >probably< already is valid, since before adding every block it is checked for validity, but
	# TODO implement to make sure the chain is really valid.
	def is_valid(self):
		for block in self.blocks:
			if not block.is_valid():
				return False

		return True

	def json(self):
		return [block.json() for block in self.blocks]

class Block(object):

	@staticmethod
	def fromJSON(json):
		obj = Block([], None)
		obj.id = json['id']
		obj.timestamp = time.gmtime(calendar.timegm(json['timestamp']))
		obj.parent_hash = b64decode(json['parent_hash']) if json['parent_hash'] else None
		obj.size = json['transaction_count']
		obj.transactions = [SmartPresence.fromJSON(t) for t in json['transactions']]
		obj.hash = b64decode(json['hash'])

		return obj

	def __init__(self, transactions, parent=None):
		self.id = parent.id + 1 if parent else 1
		self.timestamp = time.gmtime()
		self.transactions = transactions
		self.parent = parent
		self.parent_hash = self.parent.hash if self.parent else ''
		self.size = len(transactions)
		self.hash = self.to_SHA256()

	def is_valid(self):
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
			if not transaction.is_valid():
				return False

		return True

	def json(self):
		parent_hash = None

		if self.parent:
			parent_hash = b64encode(self.parent_hash).decode('utf-8')

		json_block = {
			'id': self.id,
			'timestamp' : self.timestamp,
			'parent_hash': parent_hash,
			'transaction_count': self.size,
			'transactions': [t.json() for t in self.transactions],
			'hash': b64encode(self.hash).decode('utf-8')
		}

		return json_block

	def to_SHA256(self):
		return SHA256.new(self.to_base64()).digest()

	def to_base64(self):
		parent_hash = None

		if self.parent:
			parent_hash = b64encode(self.parent_hash).decode('utf-8')

		block_content = {
			'id': self.id,
			'timestamp' : self.timestamp,
			'parent_hash': parent_hash, 
			'transaction_count': self.size, 
			'transactions': [t.json() for t in self.transactions]
		}

		return b64encode(bytes(json.dumps(block_content, sort_keys=True), 'utf-8'))