const { ethers } = require("hardhat");
const { expect } = require("chai");

describe("ModelRegistry", function () {
  it("should register models", async function () {
    const Registry = await ethers.getContractFactory("ModelRegistry");
    const reg = await Registry.deploy();
    await reg.waitForDeployment();

    await reg.registerModel("cid123", 1, '{"acc":0.90}');
    expect(await reg.totalModels()).to.equal(1);
  });
});
