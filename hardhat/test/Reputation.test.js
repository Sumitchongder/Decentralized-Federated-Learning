const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Reputation", function () {
  let reputation, owner, addr1;

  beforeEach(async () => {
    [owner, addr1] = await ethers.getSigners();
    const Reputation = await ethers.getContractFactory("Reputation");
    reputation = await Reputation.deploy();
    await reputation.deployed();
  });

  it("should add and reduce reputation", async () => {
    await reputation.addReputation(addr1.address, 10);
    expect(await reputation.getReputation(addr1.address)).to.equal(10);

    await reputation.reduceReputation(addr1.address, 5);
    expect(await reputation.getReputation(addr1.address)).to.equal(5);
  });

  it("should not go below 0", async () => {
    await reputation.reduceReputation(addr1.address, 10);
    expect(await reputation.getReputation(addr1.address)).to.equal(0);
  });
});
