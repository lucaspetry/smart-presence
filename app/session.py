# A presence registration session held by an authority.
# This is a sample application of an authority
class Session(object):

	# Constructs a new session of <id> and <name>, for the authority 
	# of <publicKey>
	def __init__(self, id, name, publicKey):
		self.id = id
		self.name = name
		self.publicKey = publicKey
		self.open = True
		self.pendingTransactions = {}
		self.approvedTransactions = {}
		self.rejectedTransactions = {}