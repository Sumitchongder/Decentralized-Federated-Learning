// SPDX-License-Identifier: MIT
pragma solidity ^0.8.21;

contract ModelRegistry {
    struct Model {
        uint256 round;
        string cid;
        address uploader;
        uint256 timestamp;
    }

    Model[] public models;

    event ModelRegistered(uint256 round, string cid, address uploader);

    function registerModel(uint256 round, string memory cid) public {
        models.push(Model(round, cid, msg.sender, block.timestamp));
        emit ModelRegistered(round, cid, msg.sender);
    }

    function getModels() public view returns (Model[] memory) {
        return models;
    }
}
