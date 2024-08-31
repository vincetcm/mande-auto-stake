# Mande Network Stake and Unstake Automation

This project allows you to perform automated staking and unstaking operations with the **TrustDrops** smart contract on the Mande network. This Python script continuously monitors the stake transactions made with the wallet addresses you specify and automatically balances the staking transactions made to your addresses.

## Required Libraries

You will need the following Python libraries to run the project:

- `web3`: We use the Web3.py library to interact with the Mande network. This library is necessary for interacting with smart contracts and performing transactions on the blockchain.
- `requests`: Used to fetch data and make queries from subgraphs connected to the Mande network.
- `decimal`: This library allows us to perform high-precision decimal calculations, especially for calculating token amounts.
- `datetime`: Used to create timestamps and schedule events.

You can install these libraries using the following commands:

```bash
pip install web3
pip install requests
pip install json
