from uuid import uuid4
import requests
from Blockchain import Blockchain
from flask import Flask, jsonify, request

# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    b = blockchain.new_transaction(
        {
            'sender':"0",
            'recipient':node_identifier,
            'amount':1,
        }
    )

	# We run the proof of work algorithm to get the next proof...
    block = blockchain.proof_of_work()

    # Forge the new Block by adding it to the chain
    blockchain.add_block(block)

    # Note: We add the reward transaction to the block then try the pow, 
    # and the reward will only be given and validiated on a good pow. 
    # This way we dont have to blast everyone the transaction and still count it
    # This might not be good though (repeated rewards, might want to add transaction verfication)

    response = {
        'message': "New Block Forged",
        'index': block.index,
        'data': block.transactions,
        'proof': block.nonce,
        'previous_hash': block.previous_hash,
    }
    return jsonify(response), 200

@app.route('/transactions', methods=['GET'])
def get_transactions():
    return jsonify(blockchain.current_transactions), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    if values is None: return 'Null data', 400
    # Check that the required fields are in the POST'ed data
    # required = ['sender', 'recipient', 'amount']
    # if not all(k in values for k in required):
    #     return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values)

    neighbours = blockchain.nodes
    for node in neighbours:
        r = requests.post('http://{node}/transactions/add'.format(node=node), json = values)

    response = {'message': 'Transaction will be added to Block {index}'.format(index=index)}
    return jsonify(response), 201

@app.route('/transactions/add', methods=['POST'])
def add_transaction():
    values = request.get_json()

    if values is None: return 'Null data', 400

    index = blockchain.new_transaction(values)

    response = {'message': 'Transaction will be added to Block {index}'.format(index=index)}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.toJson(),
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/hash', methods=['GET'])
def hash_chain():
	response = {'hash': blockchain.hash_chain()}
	return jsonify(response), 200

@app.route('/validate', methods=['GET'])
def validate():
	response = blockchain.valid_chain()
	return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    # should also maybe put a get for transactions
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.toJson()
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.toJson()
        }

    return jsonify(response), 200

@app.route('/nodes', methods=['GET'])
def get_nodes():
    response = {
        'total_nodes':list(blockchain.nodes), 
        'number_of_nodes':len(list(blockchain.nodes))
    }
    return jsonify(response, 200)




if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)














