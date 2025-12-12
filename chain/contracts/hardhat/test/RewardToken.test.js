const { ethers } = require("hardhat");
const { expect } = require("chai");

describe("RewardToken", function () {
  it("should mint and reward correctly", async function () {
    const Token = await ethers.getContractFactory("RewardToken");
    const token = await Token.deploy();
    await token.waitForDeployment();

    const [owner, user] = await ethers.getSigners();

    await token.reward(user.address, ethers.parseEther("10"));

    const bal = await token.balanceOf(user.address);
    expect(bal).to.equal(ethers.parseEther("10"));
  });
});
