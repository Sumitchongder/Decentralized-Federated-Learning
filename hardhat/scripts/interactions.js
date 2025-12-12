const hre = require("hardhat");

async function main() {
  const [user] = await hre.ethers.getSigners();

  // Connect to deployed contracts (replace addresses with deployed ones)
  const modelRegistryAddress = "<MODEL_REGISTRY_ADDRESS>";
  const rewardTokenAddress = "<REWARD_TOKEN_ADDRESS>";
  const reputationAddress = "<REPUTATION_ADDRESS>";

  const ModelRegistry = await hre.ethers.getContractFactory("ModelRegistry");
  const modelRegistry = await ModelRegistry.attach(modelRegistryAddress);

  const RewardToken = await hre.ethers.getContractFactory("RewardToken");
  const rewardToken = await RewardToken.attach(rewardTokenAddress);

  const Reputation = await hre.ethers.getContractFactory("Reputation");
  const reputation = await Reputation.attach(reputationAddress);

  // Register a new model
  let tx = await modelRegistry.registerModel(1, "QmTestCID12345");
  await tx.wait();
  console.log("Model registered");

  // Mint reward tokens
  tx = await rewardToken.mint(user.address, 1000);
  await tx.wait();
  console.log("Minted 1000 tokens to user");

  // Add reputation
  tx = await reputation.addReputation(user.address, 10);
  await tx.wait();
  console.log("Added 10 reputation points");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
