import brownie
from nacl.public import PrivateKey

from scripts.crypto import encrypt_nacl, export_public_key
from scripts.utils import get_account


def test_get_round_model(accounts, project, token):
    # Arrange
    owner = get_account()
    token.increaseAllowance(project.address, 1000, {"from": owner})
    project.changeNodeStatus(True, {"from": owner})

    # Act + Assert
    with brownie.reverts("No training plans created"):
        project.getRoundModel(0, owner)

    project.createPlan("testCID1", 10, 10, {"from": owner})
    assert project.getRoundModel(0, owner) == ""

    project.submitModel("testCID2", {"from": owner})
    assert project.getRoundModel(0, owner) == "testCID2"
    assert project.getRoundModel(0, accounts[0]) == ""

    project.submitModel("testCID3", {"from": owner})
    assert project.getRoundModel(1, owner) == "testCID3"
    assert project.getRoundModel(2, owner) == ""
    assert True


def test_abort_plan(accounts, project, token):
    # Arrange
    owner = get_account()
    token.increaseAllowance(project.address, 1000, {"from": owner})
    project.changeNodeStatus(True, {"from": owner})
    project.createPlan("testCID1", 10, 10, {"from": owner})

    # Act + Assert
    with brownie.reverts("Only creator can abort the plan"):
        project.abortPlan({"from": accounts[0]})

    assert project.isPlanRunning() is True
    project.abortPlan({"from": owner})
    assert project.isPlanRunning() is False


def test_finish_plan(accounts, project, token):
    # Arrange
    owner = get_account()
    token.increaseAllowance(project.address, 1000, {"from": owner})
    project.changeNodeStatus(True, {"from": owner})
    project.createPlan("testCID1", 2, 10, {"from": owner})
    project.submitModel("testCID2", {"from": owner})

    # Act
    with brownie.reverts("All rounds must be completed"):
        project.finishPlan("testCID3", {"from": owner})

    project.submitModel("testCID3", {"from": owner})
    project.finishPlan("testCID4", {"from": owner})
    n_plans = project.numPlans()
    plan = project.plans(n_plans - 1).dict()
    is_plan_running = project.isPlanRunning()

    # Assert
    assert n_plans == 1
    assert plan["finalModelCID"] == "testCID4"
    assert is_plan_running is False


def test_change_owner_status(project):
    # Arrange
    owner = get_account()

    # Act
    project.changeNodeStatus(True, {"from": owner})
    node = project.nodesArray(0).dict()

    # Assert
    assert node["activated"] is True


def test_change_node_status(accounts, project):
    # Arrange
    owner = get_account()
    node_address = accounts[0]

    test_key = PrivateKey.generate()
    public_key = export_public_key(bytes(test_key).hex())
    project.requestJoinNode(public_key, {"from": node_address})

    secret = b"Test" * 8
    ciphertext = encrypt_nacl(public_key, secret)
    project.acceptNode(list(ciphertext), {"from": owner})

    # Act + Assert
    node = project.nodesArray(1).dict()
    assert node["activated"] is True

    project.changeNodeStatus(False, {"from": node_address})
    node = project.nodesArray(1).dict()
    assert node["activated"] is False
