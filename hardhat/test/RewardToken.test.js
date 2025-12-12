const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("RewardToken", function () {
  let token, owner, addr1;

  beforeEach(async () => {
    [owner, addr1] = await ethers.getSigners();
    const RewardToken = await ethers.getContractFactory("RewardToken");
    token = await RewardToken.deploy();
    await token.deployed();
  });

  it("should mint and burn tokens", async () => {
    await token.mint(addr1.address, 1000);
    expect(await token.balanceOf(addr1.address)).to.equal(1000);

    await token.burn(addr1.address, 500);
    expect(await token.balanceOf(addr1.address)).to.equal(500);
  });
});
