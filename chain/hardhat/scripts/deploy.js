const { ethers } = require("hardhat");

async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with:", deployer.address);

    const Registry = await ethers.getContractFactory("ModelRegistry");
    const registry = await Registry.deploy();
    await registry.waitForDeployment();

    const Token = await ethers.getContractFactory("RewardToken");
    const token = await Token.deploy();
    await token.waitForDeployment();

    const Reputation = await ethers.getContractFactory("Reputation");
    const rep = await Reputation.deploy();
    await rep.waitForDeployment();

    console.log("ModelRegistry:", await registry.getAddress());
    console.log("RewardToken:", await token.getAddress());
    console.log("Reputation:", await rep.getAddress());
}

main().catch((e) => {
    console.error(e);
    process.exit(1);
});
