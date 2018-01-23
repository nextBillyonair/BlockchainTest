import hashlib
import json

class MerkleTree:
	def __init__(self, data):
		self.data = data
		self.merkle_tree = self.build_hash(self.data)
		self.merkle_root = self.merkle_tree[-1][0]


	def build_hash(self, data):
		if len(data) % 2 == 1 or len(data) == 0:
			data = data + ["NONE"]
		lst = [hashlib.sha1(json.dumps(item, sort_keys=True).encode()).hexdigest() for item in data]
		tree = [lst]
		while len(lst) != 1:
			if len(lst) % 2 == 1:
				lst.append(hashlib.sha1("NONE").hexdigest())
			lst = [hashlib.sha1(lst[i] + lst[i+1]).hexdigest() for i in range(0, len(lst), 2)]
			tree.append(lst)
		
		return tree


if __name__ == '__main__':
	m = MerkleTree([{"a":4}, {"b":4}, {"c":4}, {"b":4}, {"c":4}])
	print m.data
	for item in m.merkle_tree:
		print item
		print "\n"
	print m.merkle_root