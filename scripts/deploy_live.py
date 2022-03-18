from brownie import FELToken, ProjectManager, accounts, config, network

# Total supply times decimals
INITIAL_SUPPLY = 100000000000 * (10**18)


def main():
    owner = accounts.add(config["wallets"]["owner_key"])
    print(f"On network {network.show_active()}")

    feltoken = FELToken.deploy(INITIAL_SUPPLY, {"from": owner}, publish_source=True)
    ProjectManager.deploy(feltoken, {"from": owner}, publish_source=True)
