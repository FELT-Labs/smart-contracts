// SPDX-License-Identifier: GPL3
pragma solidity ^0.8.0;

import "./Builders.sol";
import "./DataProviders.sol";

/**
 * @dev A contract that manages the training plans for the project.
 * There is always only 1 plan running at a time. All the plans are
 * stored on the blockchain
 */
contract TrainingPlans is Builders, DataProviders {
    // Training Plan Round
    struct Round {
        bool completed;
        uint256 numSubmitted;
        mapping(address => string) modelsCID;
    }

    // Training Plan defines instructions for training clients (data providers)
    struct TrainingPlan {
        // bytes data;
        address creator;
        address finalNode;
        uint32 randomSeed;
        // Base model uploaded by builder
        string baseModelCID;
        // Final model uploaded by finalNode
        // Final model is encrypted using builder public key
        string finalModelCID;
        // Training params
        uint32 numRounds;
        // Number of nodes and rewards in training
        uint256 numNodes;
        uint256 totalReward;
        uint256 nodeReward;
        uint256 keyTurn;
        // mapping (acting as array) of rounds
        mapping(uint256 => Round) rounds;
    }

    mapping(uint256 => TrainingPlan) public plans;
    uint32 public numPlans = 0;

    bool public isPlanRunning = false;
    uint32 public currentRound = 0;

    // seed for pseudo random number generator
    uint256 private _seed = 7;

    function _calculateTotalReward(uint32 _rounds, uint256 _reward)
        internal
        view
        returns (uint256)
    {
        return uint256(_rounds) * _reward * activeNodes;
    }

    // TODO: Add Chainlink Keeper to close round if time elapses
    function _saveModel(string memory modelCID) internal onlyNode {
        require(
            currentRound < plans[numPlans - 1].numRounds,
            "No more rounds to perform."
        );

        Round storage round = plans[numPlans - 1].rounds[currentRound];
        require(
            bytes(round.modelsCID[msg.sender]).length == 0,
            "Model already sent for this round"
        );

        // Store model CID and finish in case it is last
        round.modelsCID[msg.sender] = modelCID;
        round.numSubmitted += 1;
        if (round.numSubmitted >= activeNodes) {
            round.completed = true;
            currentRound += 1;
        }
    }

    function getRoundModel(uint256 roundIdx, address nodeAddress)
        public
        view
        returns (string memory)
    {
        require(numPlans > 0, "No training plans created");
        return plans[numPlans - 1].rounds[roundIdx].modelsCID[nodeAddress];
    }

    function _addPlan(
        string memory modelCID,
        uint32 rounds,
        uint256 reward
    ) internal onlyBuilder {
        require(!isPlanRunning, "Another plan is already being executed");
        require(activeNodes > 0, "No active nodes to execute the plan");

        TrainingPlan storage plan = plans[numPlans++];
        plan.creator = msg.sender;
        plan.baseModelCID = modelCID;
        plan.numRounds = rounds;
        plan.numNodes = activeNodes;
        plan.nodeReward = reward;
        plan.totalReward = _calculateTotalReward(rounds, reward);
        plan.keyTurn = keyTurn;

        uint256 randNum = _getRandomNumber();

        // TODO: Deal better with inactive nodes so it is more fair
        uint256 i = randNum % nodesArray.length;
        for (; !nodesArray[i % nodesArray.length].activated; ++i) {}

        plan.finalNode = nodesArray[i % nodesArray.length]._address;
        plan.randomSeed = uint32(randNum);

        currentRound = 0;
        isPlanRunning = true;
    }

    // Abort plan
    function abortPlan() public {
        require(
            numPlans > 0 && plans[numPlans - 1].creator == msg.sender,
            "Only creator can abort the plan"
        );
        isPlanRunning = false;
    }

    // Finish plan
    // IMPORTANT: Use combination of seed and secret to generate builder secret
    // TODO add verification by other nodes
    function finishPlan(string memory modelCID) public onlyNode {
        TrainingPlan storage plan = plans[numPlans - 1];
        require(
            plan.finalNode == msg.sender,
            "Only pre-selected node can finish plan"
        );
        require(currentRound >= plan.numRounds, "All rounds must be completed");

        plan.finalModelCID = modelCID;

        isPlanRunning = false;
    }

    /** Function node can become active/inactive */
    function changeNodeStatus(bool status) public onlyNode {
        require(!isPlanRunning, "Node can't change status while plan running.");
        if (nodesArray[nodeState[msg.sender] - 3].activated != status) {
            activeNodes = (status) ? activeNodes + 1 : activeNodes - 1;
        }
        nodesArray[nodeState[msg.sender] - 3].activated = status;
    }

    // get pseudo random number
    function _getRandomNumber() private returns (uint256) {
        _seed = uint256(
            keccak256(
                abi.encodePacked(
                    _seed,
                    blockhash(block.number - 1),
                    block.coinbase,
                    block.difficulty
                )
            )
        );
        return _seed;
    }
}
