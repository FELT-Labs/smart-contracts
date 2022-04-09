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

Active deployments are listed in [`build/deployments`](build/deployments/map.json) folder.
Smart contracts are deployed automatically to Mumbai (polygon testnet) on push to main branch.
To setup remote node set in `.env`: `WEB3_INFURA_PROJECT_ID` from your infura account and `POLYGONSCAN_TOKEN` to api key from [polygonscan](https://polygonscan.com/).
To list available networks in brownie run `brownie networks list`.

- `brownie run deploy_dev` to deploy and setup test contracts
- `brownie run deploy_live --network polygon-test` to deploy on testnet
- `brownie run deploy_live --network polygon-main` to deploy on polygon main livenet

During deployment, project contract ABI (`ProjectContract.json`) is copied to `build/deployments/{chain_id}` folder
(`chain_id` stands for chain id or `dev` in case of local deployment using ganache). Project file from this folder should be used for obtaining project contract ABI.

## Development

You can use the command `brownie run deploy_dev` for local development.
This command will run ganache and http server at [`http://localhost:8100`](http://localhost:8100), providing the `build/deployments` directory.
Other applications can download contracts ABI and get deployment addresses from this server.
The code for downloading ABI should work the same for testet as local development; you only need to change the URL based on chain id (github or localhost url).