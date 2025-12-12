// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract RewardToken is ERC20 {
    address public admin;

    constructor() ERC20("PolyScale Token", "PST") {
        admin = msg.sender;
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }

    function mint(address to, uint256 amount) external {
        require(msg.sender == admin, "Only admin can mint");
        _mint(to, amount);
    }

    function burn(address from, uint256 amount) external {
        require(msg.sender == admin, "Only admin can burn");
        _burn(from, amount);
    }
}
