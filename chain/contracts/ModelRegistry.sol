// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * ModelRegistry
 * --------------
 * Stores:
 *  - model CID (from IPFS)
 *  - round number
 *  - training metrics (JSON string)
 *
 * Events allow off-chain systems (dashboard, analytics) to subscribe
 * to new global model updates.
 */

contract ModelRegistry {
    struct ModelEntry {
        string cid;
        uint256 roundNumber;
        string metricsJSON;
        uint256 timestamp;
    }

    ModelEntry[] public models;

    event ModelRegistered(
        uint256 indexed index,
        string cid,
        uint256 roundNumber,
        string metricsJSON,
        uint256 timestamp
    );

    function registerModel(
        string memory cid,
        uint256 roundNumber,
        string memory metricsJSON
    ) public returns (uint256) {

        uint256 ts = block.timestamp;
        models.push(ModelEntry(cid, roundNumber, metricsJSON, ts));

        uint256 idx = models.length - 1;
        emit ModelRegistered(idx, cid, roundNumber, metricsJSON, ts);

        return idx;
    }

    function getModel(uint256 index)
        public
        view
        returns (string memory, uint256, string memory, uint256)
    {
        ModelEntry memory m = models[index];
        return (m.cid, m.roundNumber, m.metricsJSON, m.timestamp);
    }

    function totalModels() public view returns (uint256) {
        return models.length;
    }
}
