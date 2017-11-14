from Crypto.PublicKey import RSA
from base64 import b64encode
import json

if __name__ == '__main__':
	authorities = {}

	authorities['authorities'] = {}

	private_key1 = RSA.generate(2048)
	private_key2 = RSA.generate(2048)
	private_key3 = RSA.generate(2048)
	private_key4 = RSA.generate(2048)

	authorities['authorities'][5001] = {
		'name' : 'Authority1',
		'public_key' : str(b64encode(private_key1.publickey().exportKey()).decode('utf-8')),
		'key_pair' : str(b64encode(private_key1.exportKey()).decode('utf-8'))
	}

	authorities['authorities'][5002] = {
		'name' : 'Authority2',
		'public_key' : str(b64encode(private_key2.publickey().exportKey()).decode('utf-8')),
		'key_pair' : str(b64encode(private_key2.exportKey()).decode('utf-8'))
	}

	authorities['authorities'][5003] = {
		'name' : 'Authority3',
		'public_key' : str(b64encode(private_key3.publickey().exportKey()).decode('utf-8')),
		'key_pair' : str(b64encode(private_key3.exportKey()).decode('utf-8'))
	}

	authorities['authorities'][5004] = {
		'name' : 'Authority4',
		'public_key' : str(b64encode(private_key4.publickey().exportKey()).decode('utf-8')),
		'key_pair' : str(b64encode(private_key4.exportKey()).decode('utf-8'))
	}

	with open("authorities.json", "w") as file:
		json.dump(authorities, file, sort_keys=True, indent=4)