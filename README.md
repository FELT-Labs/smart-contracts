# smart-contracts

Smart contracts for federated learning written in solidity

## Setup

1. `npm install -g ganache-cli` to install [ganache-cli](https://www.npmjs.com/package/ganache-cli)
2. `pip install -r requirements.txt` to install python dependencies
3. `cp .env-template .env` to create file with environment variables
4. `pre-commit install` to install pre-commit hook for linting

## Commands

- `brownie compile` to compile smart contracts
- `brownie test` to run tests
- `brownie run deploy_live --network {network-name}` to deploy on live network
