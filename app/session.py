
class Session(object):

	def __init__(self, id, name, publicKey):
		self.id = id
		self.name = name
		self.publicKey = publicKey
		self.open = True
		self.pendingTransactions = []
		self.approvedTransactions = []