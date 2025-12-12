require("@nomiclabs/hardhat-ethers");

module.exports = {
  solidity: "0.8.20",
  networks: {
    hardhat: {},
    local: {
      url: "http://127.0.0.1:8545"
    }
  }
};
