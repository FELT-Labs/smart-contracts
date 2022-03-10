import pytest
from scripts.crypto import encrypt_nacl, export_public_key
from scripts.utils import get_account
from web3 import Web3


@pytest.fixture(autouse=True)
def setup(fn_isolation):
    """
    Isolation setup fixture.
    This ensures that each test runs against the same base environment.
    """
    pass


@pytest.fixture(scope="module")
def token(FELToken):
    """
    Yield a `Contract` object for the FELToken contract.
    """
    yield FELToken.deploy(1000, {"from": get_account()})


@pytest.fixture(scope="module")
def manager(ProjectManager, token):
    """
    Yield a `Contract` object for the ContractManager contract.
    """
    yield ProjectManager.deploy(token, {"from": get_account()})


@pytest.fixture(scope="module")
def project(ProjectContract, token):
    """
    Yield a `Contract` object for the ProjectContract contract.
    """
    owner = get_account()
    public_key = export_public_key(owner.private_key[2:])

    secret = b"Initial secret must be 32 bytes."
    ciphertext = encrypt_nacl(public_key, secret)

    project = ProjectContract.deploy(
        token, public_key, list(ciphertext), {"from": get_account()}
    )

    yield project


@pytest.fixture(scope="module")
def w3():
    return Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
