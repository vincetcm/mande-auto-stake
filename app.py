import json
from web3 import Web3
import time
import requests
from decimal import Decimal
import datetime



private_keys = ["b0982aPRIVATEKEY-1", "b0982aPRIVATEKEY-2"]
my_addresses = ["0x6b5ADDRESS-1", "0xFadADDRESS-2"]

web3 = Web3(Web3.HTTPProvider('https://mande-mainnet.public.blastapi.io:443/'))

with open('TrustDrops.json', 'r') as abi_file:
    contract_abi = json.load(abi_file)

contract_address = Web3.to_checksum_address('0xf9A67460Cd94B9F098ef211c8E46Ee27CDDEbb46')
target_contract_address = Web3.to_checksum_address('0x7Fa2Addd4d59366AA98F66861d370C174DC00B46')

def stake(i, address, amount):
    try:
        nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(my_addresses[i]))
        tx_data = '0x26476204000000000000000000000000' + address[2:]
        tx_data_bytes = Web3.to_bytes(hexstr=tx_data)
        
        tx = {
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': Web3.to_wei(5, 'gwei'),
            'to': target_contract_address,
            'value': amount,
            'data': tx_data_bytes,
            'chainId': 18071918,
        }
        
        signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_keys[i])
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Staking from: {my_addresses[i]} ADDRESS: {address} VALUE: {amount}")
        
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if tx_receipt.status == 1:
            print(f"Staking transaction successful: {tx_hash.hex()}")
            return True
        else:
            print(f"Staking transaction failed: {tx_hash.hex()}")
            return False
    except Exception as e:
        print(f"Error sending stake transaction: {e}")
        return False


def unstake(i, address, amount):
    try:
        nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(my_addresses[i]))
        tx_data = '0xc2a672e0000000000000000000000000' + address[2:] + addZeros(hex(amount)[2:])
        tx_data_bytes = Web3.to_bytes(hexstr=tx_data)
        
        tx = {
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': Web3.to_wei(5, 'gwei'),
            'to': target_contract_address,
            'data': tx_data_bytes,
            'chainId': 18071918,
        }
        
        signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_keys[i])
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Unstaking from: {my_addresses[i]} ADDRESS: {address} VALUE: {amount}")
        
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if tx_receipt.status == 1:
            print(f"Unstaking transaction successful: {tx_hash.hex()}")
            return True
        else:
            print(f"Unstaking transaction failed: {tx_receipt}")
            return False
    except Exception as e:
        print(f"Error sending unstake transaction: {e}")
        return False

def addZeros(text):
    count = 64 - len(text)
    for i in range(0, count):
        text = '0' + text
    return text

def getUnreturnedStakes(i):
    url = 'https://app.mande.network/subgraphs/name/TrustDrops'
    receivedStakesReq = {
        "operationName": "ReceivedStakesQuery",
        "query": "query ReceivedStakesQuery($address: String!) {\n  stakes(first:1000, where: {candidate_: {id: $address}}) {\n    amount\n    credScore\n    staker {\n      id\n      __typename\n    }\n    __typename\n  }\n}",
        "variables": {
            "address": my_addresses[i]
        }
    }
    stakesReq = {
        "operationName": "MyStakesQuery",
        "query": "query MyStakesQuery($address: String!) {\n  stakes(first:1000, where: {staker_: {id: $address}}) {\n    amount\n    credScore\n    candidate {\n      id\n      __typename\n    }\n    __typename\n  }\n}",
        "variables": {
            "address": my_addresses[i]
        }
    }

    try:
        stakesMap = {}
        receivedStakesMap = {}

        
        skip = 0
        while True:
            stakesReq['query'] = f"query MyStakesQuery($address: String!) {{\n  stakes(first:1000, skip:{skip}, where: {{staker_: {{id: $address}}}}) {{\n    amount\n    credScore\n    candidate {{\n      id\n      __typename\n    }}\n    __typename\n  }}\n}}"
            stakesRes = requests.post(url, json=stakesReq)

            if stakesRes.status_code != 200:
                print(f"Failed to fetch stakes data: {stakesRes.status_code}")
                return {}

            stakes = stakesRes.json().get('data', {}).get('stakes', [])
            if not stakes:
                break

            for stake in stakes:
                amount = web3.from_wei(Decimal(stake['amount']), 'ether')
                address = stake['candidate']['id']
                stakesMap[address] = amount

            skip += 1000

        
        skip = 0
        while True:
            receivedStakesReq['query'] = f"query ReceivedStakesQuery($address: String!) {{\n  stakes(first:1000, skip:{skip}, where: {{candidate_: {{id: $address}}}}) {{\n    amount\n    credScore\n    staker {{\n      id\n      __typename\n    }}\n    __typename\n  }}\n}}"
            receivedStakesRes = requests.post(url, json=receivedStakesReq)

            if receivedStakesRes.status_code != 200:
                print(f"Failed to fetch received stakes data: {receivedStakesRes.status_code}")
                return {}

            receivedStakes = receivedStakesRes.json().get('data', {}).get('stakes', [])
            if not receivedStakes:
                break

            for stake in receivedStakes:
                amount = web3.from_wei(Decimal(stake['amount']), 'ether')
                address = stake['staker']['id']
                receivedStakesMap[address] = amount

            skip += 1000

        
        unreturnedStakes = {}
        for address in set(list(stakesMap.keys()) + list(receivedStakesMap.keys())):
            if address in my_addresses:
                continue

            myStakeAmount = stakesMap.get(address, Decimal(0))
            receivedStakeAmount = receivedStakesMap.get(address, Decimal(0))

            if myStakeAmount > receivedStakeAmount:
                unstakeAmount = myStakeAmount - receivedStakeAmount
                unreturnedStakes[address] = -unstakeAmount
            elif myStakeAmount < receivedStakeAmount:
                stakeAmount = receivedStakeAmount - myStakeAmount
                unreturnedStakes[address] = stakeAmount

        return unreturnedStakes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stakes data: {e}")
        return {}

def print_status():
    now = datetime.datetime.now()
    print(f"\r[{now.strftime('%Y-%m-%d %H:%M:%S')}] Waiting for changes... ", end='', flush=True)

def manage_stake_addresses():
    processed_addresses = set()
    while True:
        try:
            length = len(private_keys)
            for i in range(0, length):
                unreturnedStakes = getUnreturnedStakes(i)
                if unreturnedStakes:
                    print(f"\nUnreturned Stakes: {unreturnedStakes}")
                for key in unreturnedStakes.keys():
                    amount = unreturnedStakes[key]
                    if amount == 0:
                        continue
                    if key in processed_addresses:
                        print(f"Skipping {key} to avoid repeated operations")
                        continue
                    if amount > 0:
                        print(f"Attempting to stake: {key} VALUE: {amount}")
                        if stake(i, key, web3.to_wei(amount, 'ether')):
                            processed_addresses.add(key)
                    else:
                        print(f"Attempting to unstake: {key} VALUE: {-amount}")
                        if unstake(i, key, web3.to_wei(-amount, 'ether')):
                            processed_addresses.add(key)
            time.sleep(30)
            processed_addresses.clear()  
            print_status()
        except Exception as e:
            print(f"\nError in manage_stake_addresses loop: {e}")
            time.sleep(30)  

if __name__ == "__main__":
    print_status()
    manage_stake_addresses()
