// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

contract Reputation {
    mapping(address => uint256) public reputation;

    event ReputationUpdated(address indexed user, uint256 newScore);

    function addReputation(address user, uint256 score) external {
        reputation[user] += score;
        emit ReputationUpdated(user, reputation[user]);
    }

    function reduceReputation(address user, uint256 score) external {
        if(reputation[user] < score) {
            reputation[user] = 0;
        } else {
            reputation[user] -= score;
        }
        emit ReputationUpdated(user, reputation[user]);
    }

    function getReputation(address user) external view returns (uint256) {
        return reputation[user];
    }
}
