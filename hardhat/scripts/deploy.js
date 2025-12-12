const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);

  const ModelRegistry = await hre.ethers.getContractFactory("ModelRegistry");
  const modelRegistry = await ModelRegistry.deploy();
  await modelRegistry.deployed();
  console.log("ModelRegistry deployed to:", modelRegistry.address);

  const RewardToken = await hre.ethers.getContractFactory("RewardToken");
  const rewardToken = await RewardToken.deploy();
  await rewardToken.deployed();
  console.log("RewardToken deployed to:", rewardToken.address);

  const Reputation = await hre.ethers.getContractFactory("Reputation");
  const reputation = await Reputation.deploy();
  await reputation.deployed();
  console.log("Reputation deployed to:", reputation.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
