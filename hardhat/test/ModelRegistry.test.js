const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ModelRegistry", function () {
  let modelRegistry, owner;

  beforeEach(async () => {
    [owner] = await ethers.getSigners();
    const ModelRegistry = await ethers.getContractFactory("ModelRegistry");
    modelRegistry = await ModelRegistry.deploy();
    await modelRegistry.deployed();
  });

  it("should register a model", async function () {
    await modelRegistry.registerModel(1, "QmTestCID123");
    const models = await modelRegistry.getModels();
    expect(models.length).to.equal(1);
    expect(models[0].cid).to.equal("QmTestCID123");
  });
});
