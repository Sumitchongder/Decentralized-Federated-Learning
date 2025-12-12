// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * Reputation
 * ----------
 * Simple on-chain reputation scoring system.
 */

contract Reputation {
    mapping(address => uint256) public scores;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function setReputation(address node, uint256 score) public {
        require(msg.sender == owner, "Not authorized");
        scores[node] = score;
    }

    function getReputation(address node) public view returns (uint256) {
        return scores[node];
    }
}
