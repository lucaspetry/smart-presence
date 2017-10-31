import hashlib
import json
import random

class Blockchain():
	def __init__(self, max_block_size, starting_accounts):
		self.max_block_size = max_block_size
		self.blocks = [Block([Transaction(starting_accounts)], 0)]
		self.accounts_state = starting_accounts
		self.pending_transactions = []

	# Function to add a single block to the chain
	def add_block(self, block):
		if block.is_valid(self.accounts_state, self.last_block()):
			self.blocks.append(block)
		else:
			# Show error message
			return

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

class Block():
	def __init__(self, transactions, id, parent=None):
		self.transactions = transactions
		self.id = id
		self.parent = parent
		self.parent_hash = parent.hash if parent is not None else None
		self.size = len(transactions)
		self.hash = self.calculate_hash()


	# Checks if all transactions in block follows these rules:
	# 1. All transactions are valid;
	# 2. Block hash is valid;
	# 3. Block id is exactly 1 higher than parent's id;
	# 4. Block has the correct parent hash.
	# In case the block is the first in the chain, only (1) and (2) apply.
	# 
	def is_valid(self, current_accounts_state):
		state = current_accounts_state.copy()

		# Rule (1)
		for transaction in self.transactions:
			if transaction.is_valid(state):
				state = transaction.execute(state)
			else:
				return False

		# Rule (2)
		if self.hash != self.calculate_hash():
			return False

		if self.parent is not None:
			# Rule (3)
			if self.id - self.parent.id != 1:
				return False

			# Rule (4)
			if self.parent.hash != self.parent_hash:
				return False

		return True

	# Transfer credits between transaction participants and return the updated accounts state
	def execute_transaction(self, transaction, accounts_state):
		return transaction.execute(accounts_state)

	# Returns the accounts state after executing every transaction in the block
	def get_final_state(self, accounts_state_before):
		state = accounts_state_before.copy()

		for transaction in self.transactions:
			state = transaction.execute(state)

		return state

	# Returns the jsonified version of the block
	def jsonify(self):
		json_block = {
			'id': self.id,
			'parent_hash': self.parent_hash if self.parent_hash is not None else '',
			'transaction_count': self.size,
			'transactions': [t.transaction for t in self.transactions],
			'hash': self.hash
		}

		return json_block

	# Hash function wrapper
	# Key ordering is necessary to make sure 
	# 	{'a': 0, 'b': 0} 
	# has the same hash as 
	# 	{'b': 0, 'a': 0}
	# since both are the same.
	def calculate_hash(self):
		block_content = {
			'id': self.id, 
			'parent_hash': self.parent_hash, 
			'transaction_count': self.size, 
			'transactions': [t.transaction for t in self.transactions]
		}

		json.dumps(block_content, sort_keys=True)
		return hashlib.sha256(str(block_content).encode('utf-8')).hexdigest()


# Transaction must always be in the following format:
# {'Participant1': <amount1>, 'Participant2': <amount2>, ..., 'ParticipantN': <amountN>}
class Transaction():
	def __init__(self, transaction):
		self.transaction = transaction

	# (Initial) Rules for a transaction to be valid:
	# 1. The sum of the paying and receiving sides must be 0, i.e the transaction can't create nor destroy money.
	# 2. Person paying has to have enough money to do so
	def is_valid(self, accounts_state):
		# Rule (1)
		if sum(self.transaction.values()) is not 0:
			return False

		# Rule (2)
		for person in self.transaction:
			amount = self.transaction[person]
			
			balance = 0
			if person in accounts_state:
				balance = accounts_state[person]
			
			if balance + amount < 0:
				return False

		return True

	def execute(self, accounts_state):
		state = accounts_state.copy()

		for person in self.transaction:
			amount = self.transaction[person]

			if person in state:
				state[person] += amount
			else:
				state[person] = amount

		return state

# A transaction looks like this:
# 	{'Alice': 15, 'Bob': -15}
# This means that Bob pays Alice 15 credits.
# The following function exists to create random transactions to facilitate the testing process.
def make_transaction(max_value=5):
	# Randomly chooses between -1 and 1
	sign = int(random.getrandbits(1))*2-1

	amount = random.randint(1, max_value)
	alice_pays = sign * amount
	bob_pays = -1 * alice_pays

	return Transaction({'Alice': alice_pays, 'Bob': bob_pays})

if __name__ == '__main__':
	chain = Blockchain(5, {'Alice': 5, 'Bob': 5})
	transactions = [make_transaction() for i in range(30)]

	chain.add_transactions(transactions)
	json = chain.jsonify()