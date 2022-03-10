// SPDX-License-Identifier: GPL3
pragma solidity ^0.8.0;

import "./FELToken.sol";
import "./project/TrainingPlans.sol";

// TODO: Make interface/abstract project contract

/**
 * @title Project Contract
 * @notice Project Contract manages references to Data Providers (nodes) and
 * Builders (scientists). Data providers must watch this contract and execute
 * new plans. Builders creat training plans.
 * @dev This contract is instantiated for each project and can be edited for individual needs.
 */
contract ProjectContract is TrainingPlans {
    FELToken private token;

    /**
     * @dev Initializes the project. Creator becomes both builder and data provider, might be changed in future
     * @param _token address of the FELToken
     * @param publicKey - Builder setup
     * @param secret - Encrypted secret for the owner (owner encrypts for himself)
     */
    constructor(
        FELToken _token,
        bytes32 publicKey,
        bytes[112] memory secret
    ) {
        token = _token;

        builders[msg.sender] = Builder({
            _address: msg.sender,
            publicKey: publicKey
        });
        buildersArray.push(msg.sender);

        nodeState[msg.sender] = 3;
        nodesArray.push(
            Node({
                _address: msg.sender,
                activated: false,
                secret: secret,
                entryKeyTurn: 0
            })
        );
    }

    /**
     * @notice Builder creates training plan
     * @param modelCID - ipfs CID
     * @param rounds - number of training rounds
     * @param reward - reward for data providers for each model submitted
     */
    function createPlan(
        string memory modelCID,
        uint32 rounds,
        uint256 reward
    ) public {
        _addPlan(modelCID, rounds, reward);

        // Builder has to provide the reward
        uint256 totalReward = _calculateTotalReward(rounds, reward);
        token.transferFrom(msg.sender, address(this), totalReward);
    }

    /**
     * @notice Data provider submits model
     * @param modelCID - ipfs CID
     */
    function submitModel(string memory modelCID) public {
        _saveModel(modelCID);

        // Send reward to node
        token.transfer(msg.sender, plans[numPlans - 1].nodeReward);
        plans[numPlans - 1].totalReward -= plans[numPlans - 1].nodeReward;
    }

    /** TODO:
     *    - Sponsor projects
     *    - Request/Buy model
     *    - Validation
     *    - Settings public/private
     *        - possible to join for new nodes/builders
     */

    // Vote for removing fake node
    //   - Also must reestablish the secret
    // function voteNodeRemove(address _address) public onlyNode {
    //    // TODO: check if already voted
    //    // Increment vote count of node, kick if vote count above half
    // }
}
