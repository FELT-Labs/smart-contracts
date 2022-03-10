import brownie
from nacl.public import PrivateKey

from scripts.crypto import export_public_key
from scripts.utils import get_account


def test_owner_is_builder(project):
    # Arrange
    owner = get_account()

    # Act
    builder = project.builders(owner).dict()

    # Assert
    assert builder["_address"] == owner


def test_set_builder_public_key(accounts, project):
    # Arrange
    owner = get_account()
    non_builder = accounts[0]

    # Act
    test_key = PrivateKey.generate()
    public_key = export_public_key(bytes(test_key).hex())
    project.setBuilderPublickey(public_key, {"from": owner})
    builder = project.builders(owner).dict()

    # Assert
    assert builder["publicKey"].hex() == bytes(test_key.public_key).hex()
    assert builder["_address"] == owner

    with brownie.reverts("Sender is not builder"):
        project.setBuilderPublickey(public_key, {"from": non_builder})


def test_add_builder(accounts, project):
    # Arrange
    owner = get_account()
    new_builder_address = accounts[0]

    # Act
    test_key = PrivateKey.generate()
    public_key = export_public_key(bytes(test_key).hex())
    project.addBuilder(new_builder_address, public_key, {"from": owner})

    # Assert
    assert project.getBuildersLength() == 2
    assert project.buildersArray(0) == owner
    assert project.buildersArray(1) == new_builder_address

    new_builder = project.builders(new_builder_address).dict()
    assert new_builder["_address"] == new_builder_address
    assert new_builder["publicKey"].hex() == bytes(test_key.public_key).hex()

    with brownie.reverts("Builder already exists"):
        project.addBuilder(new_builder_address, public_key, {"from": owner})

    with brownie.reverts("Only builders are allowed to execute this."):
        project.addBuilder(new_builder_address, public_key, {"from": accounts[1]})


def test_request_join_builder(accounts, project):
    # Arrange
    owner = get_account()
    requestor = accounts[0]

    # Act
    test_key = PrivateKey.generate()
    public_key = export_public_key(bytes(test_key).hex())
    project.requestJoinBuilder(public_key, {"from": requestor})

    # Assert
    assert project.getBuilderRequestsLength() == 1
    assert project.builderRequestsArray(0) == requestor

    request = project.builderRequests(requestor).dict()
    assert request["builderAddress"] == requestor
    assert request["publicKey"].hex() == public_key.hex()
    assert request["index"] == 0

    with brownie.reverts("Builder already requested join"):
        project.requestJoinBuilder(public_key, {"from": requestor})

    with brownie.reverts("Builder already exists"):
        project.requestJoinBuilder(public_key, {"from": owner})


def test_accept_request_join_builder(accounts, project):
    # Arrange
    owner = get_account()
    requestor = accounts[0]

    # Act
    test_key = PrivateKey.generate()
    public_key = export_public_key(bytes(test_key).hex())
    project.requestJoinBuilder(public_key, {"from": requestor})
    project.acceptBuilderJoinRequest(requestor, {"from": owner})

    # Assert
    assert project.getBuilderRequestsLength() == 0

    assert project.getBuildersLength() == 2
    assert project.buildersArray(0) == owner
    assert project.buildersArray(1) == requestor

    new_builder = project.builders(requestor).dict()
    assert new_builder["_address"] == requestor
    assert new_builder["publicKey"].hex() == public_key.hex()

    with brownie.reverts(
        "Address of new builder hasn't created request. Consider using addBuilder."
    ):
        project.acceptBuilderJoinRequest(accounts[1], {"from": owner})

    with brownie.reverts("Only builders are allowed to execute this."):
        project.acceptBuilderJoinRequest(requestor, {"from": accounts[1]})


def test_decline_request_join_builder(accounts, project):
    # Arrange
    owner = get_account()
    requestor = accounts[0]

    # Act
    test_key = PrivateKey.generate()
    public_key = export_public_key(bytes(test_key).hex())
    project.requestJoinBuilder(public_key, {"from": requestor})
    project.declineBuilderJoinRequest(requestor, {"from": owner})

    # Assert
    assert project.getBuilderRequestsLength() == 0

    assert project.getBuildersLength() == 1
    assert project.buildersArray(0) == owner

    with brownie.reverts(
        "Address of new builder hasn't created request. Consider using addBuilder."
    ):
        project.declineBuilderJoinRequest(accounts[1], {"from": owner})

    with brownie.reverts("Only builders are allowed to execute this."):
        project.declineBuilderJoinRequest(requestor, {"from": accounts[1]})


def test_removing_requests(accounts, project):
    # Arrange
    owner = get_account()
    requestor0 = accounts[0]
    requestor1 = accounts[1]
    requestor2 = accounts[2]
    requestor3 = accounts[3]

    # Act
    test_key = PrivateKey.generate()
    public_key = export_public_key(bytes(test_key).hex())
    project.requestJoinBuilder(public_key, {"from": requestor0})
    project.requestJoinBuilder(public_key, {"from": requestor1})
    project.requestJoinBuilder(public_key, {"from": requestor2})
    project.requestJoinBuilder(public_key, {"from": requestor3})

    # Assert
    assert project.getBuilderRequestsLength() == 4
    assert project.builderRequestsArray(0) == requestor0
    assert project.builderRequestsArray(1) == requestor1
    assert project.builderRequestsArray(2) == requestor2
    assert project.builderRequestsArray(3) == requestor3

    # delete 0 and move 3 in place of 0
    project.declineBuilderJoinRequest(requestor0, {"from": owner})
    assert project.getBuilderRequestsLength() == 3
    assert project.builderRequestsArray(0) == requestor3
    assert project.builderRequestsArray(1) == requestor1
    assert project.builderRequestsArray(2) == requestor2
    with brownie.reverts(""):
        project.builderRequestsArray(3)

    # delete 1 and move 2 in place of 1
    project.declineBuilderJoinRequest(requestor1, {"from": owner})
    assert project.getBuilderRequestsLength() == 2
    assert project.builderRequestsArray(0) == requestor3
    assert project.builderRequestsArray(1) == requestor2

    # delete 2 as last element so nothing moves
    project.declineBuilderJoinRequest(requestor2, {"from": owner})
    assert project.getBuilderRequestsLength() == 1
    assert project.builderRequestsArray(0) == requestor3

    # delete last element
    project.declineBuilderJoinRequest(requestor3, {"from": owner})
    assert project.getBuilderRequestsLength() == 0
