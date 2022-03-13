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

## Deploy

Active deployments on testnet are in [`build/deployments`](build/deployments/map.json) folder.
Smart contracts are deployed automatically to Mumbai (polygon testnet) on push to main branch.
To setup remote node set in `.env`: `WEB3_INFURA_PROJECT_ID` from your infura account and `POLYGONSCAN_TOKEN` to api key from [polygonscan](https://polygonscan.com/).
To list available networks in brownie run `brownie networks list`.

- `brownie run deploy_dev` to deploy and setup test contracts
- `brownie run deploy_live --network polygon-test` to deploy on testnet
- `brownie run deploy_live --network polygon-main` to deploy on polygon main livenet
