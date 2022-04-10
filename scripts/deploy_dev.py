from brownie import FELToken, ProjectManager, accounts, config, network

from scripts.project import deploy_project, setup_test_project
from scripts.utils import copy_project_contract, server_build_directory

# Total supply times decimals
INITIAL_SUPPLY = 100000000000 * (10**18)


def main():
    owner = accounts.add(config["wallets"]["owner_key"])
    accounts[0].transfer(owner, "3 ether")
    print(f"On network {network.show_active()}")

    feltoken = FELToken.deploy(INITIAL_SUPPLY, {"from": owner})
    ProjectManager.deploy(feltoken, {"from": owner})

    # Setup test project
    project = deploy_project(owner)
    setup_test_project(project, owner)
    # Print instructions for testing
    print("Connect test data provider as (change account and data as needed):")
    print(f"felt-node-worker --chain 1337 --contract {project} --account node1 --data test")

    # Copy project contract for serving to web app / python client
    copy_project_contract(network.chain.id)

    # Serve build directory for local development
    server_build_directory()
