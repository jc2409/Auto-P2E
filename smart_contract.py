from flask import Flask, request, jsonify
from web3 import Web3
import json, os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Load ENV variables
INFURA_URL = os.getenv("INFURA_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT_ADDRESS = Web3.to_checksum_address(os.getenv("ACCOUNT_ADDRESS"))
CONTRACT_ADDRESS = Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))

print(INFURA_URL)
print(PRIVATE_KEY)
print(ACCOUNT_ADDRESS)
print(CONTRACT_ADDRESS)

# Connect to Web3
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
assert w3.is_connected(), "Web3 connection failed"

# Load ABI
with open("abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# Endpoint: Reward a user
@app.route("/reward", methods=["POST"])
def reward_user():
    data = request.get_json()
    user_address = data.get("user_address")
    if not user_address:
        return jsonify({"error": "Missing user_address"}), 400

    try:
        user_address = Web3.to_checksum_address(user_address)
        nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)

        txn = contract.functions.rewardUser(user_address).build_transaction({
            "from": ACCOUNT_ADDRESS,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.to_wei("20", "gwei")
        })

        signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        return jsonify({
            "transaction_hash": tx_hash.hex(),
            "status": "Reward sent",
            "blockNumber": receipt.blockNumber
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Optional: Get contract balance
@app.route("/balance", methods=["GET"])
def get_balance():
    try:
        balance = contract.functions.getBalance().call()
        return jsonify({"contract_balance": w3.from_wei(balance, "ether")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
