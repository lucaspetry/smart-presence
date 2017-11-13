import json
import random
import Crypto.Hash.SHA256 as SHA256
from base64 import b64encode, b64decode 

class Blockchain(object):

	def __init__(self, block_size):
		self.block_size = block_size
		self.blocks = [Block([Transaction(starting_accounts)], 0)]
		self.pending_transactions = []

	# Function to add a single block to the chain
	def add_block(self, block):
		if block.is_valid(self.accounts_state, self.last_block()):
			self.blocks.append(block)
			return True
		
		return False

	# Function to add all transactions, creating the blocks inside the function
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
		pass

	def jsonify(self):
		return [block.jsonify() for block in self.blocks]

class Block(object):

	def __init__(self, id, transactions, parent=None):
		self.id = id
		self.transactions = transactions
		self.parent = parent
		self.parent_hash = self.parent.hash if self.parent else ''
		self.size = len(transactions)
		self.hash = self.to_SHA256()

	def is_valid(self, current_accounts_state):
		# Block ID is greater than parent ID by 1
		if self.parent and self.id - self.parent.id != 1:
			return False

		# Stored parent hash is equals to actual parent hash
		if self.parent and self.parent.hash != self.parent_hash:
			return False

		# Stored hash is equals to generated block hash
		if self.hash != self.to_SHA256():
			return False

		# All transactions are valid
		for transaction in self.transactions:
			if not transaction.is_valid():
				return False

		return True

	def jsonify(self):
		json_block = {
			'id': self.id,
			'parent_hash': self.parent_hash,
			'transaction_count': self.size,
			'transactions': [t for t in self.transactions],
			'hash': self.hash
		}

		return json_block

	def to_SHA256(self):
		return SHA256.new(self.to_base64()).digest()

	def to_base64(self):
		block_content = {
			'id': self.id, 
			'parent_hash': self.parent_hash, 
			'transaction_count': self.size, 
			'transactions': [t for t in self.transactions]
		}

		print(block_content) # Verify if it needs to be sorted
		return b64encode(bytes(block_content, 'utf-8'))



if __name__ == '__main__':
	chain = Blockchain(5, {'Alice': 5, 'Bob': 5})
	transactions = [make_transaction() for i in range(30)]

	chain.add_transactions(transactions)
	json = chain.jsonify()