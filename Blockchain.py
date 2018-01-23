import hashlib
from time import time
import json
import os
import requests
# from urllib.parse import urlparse
from urlparse import urlparse
from MerkleTree import MerkleTree
from uuid import uuid4

class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, nonce):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        # self.merkle_root = MerkleTree(self.transactions).merkle_root
        self.hash = self.hash_block()
        
      
    def hash_block(self):
        block_string = json.dumps(self.toJson(), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def toJson(self):
        return {
            'index' : self.index,
            'timestamp' : self.timestamp,
            'transactions' : self.transactions,
            'nonce' : self.nonce,
            'previous_hash' : self.previous_hash,
            # 'merkle_root': self.merkle_root
        }

    def __str__(self):
        json_obj = self.toJson()
        json_obj['hash'] = self.hash
        return json.dumps(json_obj, sort_keys=True).encode()

class Blockchain:
    def __init__(self):
        self.current_transactions = list()
        self.chain = list()
        self.nodes = set()

        # Create Gensis Block
        genesis_block = Block(
            len(self.chain), 
            time(), 
            list(), 
            "0", 
            int(os.urandom(4).encode('hex'), 16)
        )
        self.chain.append(genesis_block)

    def last_block(self):
        return self.chain[-1]

    def new_transaction(self, data):
        """
        Creates a new transaction to go into the next mined Block
        :param data: Data for transaction to be added
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append(data)
        return self.last_block().index + 1

    def proof_of_work(self):
        nonce = 0
        t_time = time()
        previous_hash = self.chain[-1].hash
        transactions = self.current_transactions
        self.current_transactions = list()

        block = Block(
            len(self.chain), 
            t_time, 
            transactions, 
            previous_hash, 
            nonce
        )
        while self.valid_proof(block) is False:
            nonce += 1
            block.nonce = nonce
            block.hash = block.hash_block()
        return block

    def add_block(self, block):
        if not self.valid_proof(block) or block.previous_hash != self.last_block().hash: 
            return None
        self.chain.append(block)
        return block

    def valid_proof(self, block):
        guess = json.dumps(block.toJson(), sort_keys=True).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        # should automate the security parameter
        return guess_hash[:4] == "0000"


    def valid_chain(self, chain=None):
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """
        if not chain: chain = self.chain

        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print('{last_block}'.format(last_block=last_block))
            print('{block}'.format(block=block))
            print("\n-----------\n")

            # Check that the hash of the block is correct
            if block.previous_hash != last_block.hash_block():
                return False

            # Check that the Proof of Work is correct
            # if not self.valid_proof(last_block.proof, block.proof):
            #     return False
            if not self.valid_proof(block):
                return False
            
            last_block = block

            current_index += 1

        return True

    def size(self):
        return len(self.chain)

    def toJson(self):
        return [block.toJson() for block in self.chain]

    def hash_chain(self):
        chain_string = json.dumps(self.toJson(), sort_keys=True).encode()
        return hashlib.sha256(chain_string).hexdigest()

    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # add resolve conflicts
    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get('http://{node}/chain'.format(node=node))

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                chain = [
                    Block(block['index'], block['timestamp'], block['transactions'], block['previous_hash'], block['nonce']) 
                    for block in chain
                ]

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain=chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False












if __name__ == '__main__':
    bc = Blockchain()
    # print bc.last_block().hash_block()
    # print bc.new_transaction([9])
    # print bc.current_transactions
    # p_o_w = bc.proof_of_work(bc.last_block().proof)
    # print p_o_w
    # print bc.valid_proof(bc.last_block().proof, p_o_w)

    # bc.new_block(p_o_w)

    # print bc.chain[0].hash
    # print bc.chain[1].previous_hash
    # print bc.current_transactions
    # print bc.chain[0].index
    # print bc.chain[1].index
    # print "\n\n\n"
    print "Gensis Valid: ", bc.valid_chain()

    for _ in range(3):
        p_o_w = bc.proof_of_work()
        print "Block POW:", str(p_o_w)
        bc.add_block(p_o_w)

    print "Size: ", bc.size()
    print "\n"
    print bc.valid_chain()
    print "\n"

    print "Hash: ", bc.hash_chain()
    # print "MR:", bc.chain[2].merkle_root
    # bc.chain[3].data = {'amt':4}
    # print bc.valid_chain()




    

