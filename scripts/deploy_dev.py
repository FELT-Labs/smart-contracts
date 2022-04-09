from brownie import FELToken, ProjectManager, accounts, config, network

from scripts.utils import copy_project_contract, server_build_directory

# Total supply times decimals
INITIAL_SUPPLY = 100000000000 * (10**18)


def main():
    owner = accounts.add(config["wallets"]["owner_key"])
    print(f"On network {network.show_active()}")

    # TODO: Provide intial supply to other accounts (node1, node2)
    accounts[0].transfer(owner, "3 ether")

    feltoken = FELToken.deploy(INITIAL_SUPPLY, {"from": owner})
    ProjectManager.deploy(feltoken, {"from": owner})

    # Copy project contract for serving to web app / python client
    copy_project_contract(network.chain.id)

    # Serve build directory for local development
    server_build_directory()
