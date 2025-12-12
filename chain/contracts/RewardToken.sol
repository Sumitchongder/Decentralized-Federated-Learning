// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * RewardToken (POLY)
 * ------------------
 * ERC20 token used to reward FL client participation.
 */

contract RewardToken is ERC20 {
    address public owner;

    constructor() ERC20("PolyScale FL Token", "POLY") {
        owner = msg.sender;
        _mint(owner, 1_000_000 ether);
    }

    function reward(address to, uint256 amount) public {
        require(msg.sender == owner, "Not authorized");
        _mint(to, amount);
    }
}
