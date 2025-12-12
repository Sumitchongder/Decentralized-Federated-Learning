import pytest
from chain.contract import FLContract

def test_commit_and_query():
    contract = FLContract()
    cid = "QmTestCID123"
    tx_hash = contract.commit_update(cid)
    
    history = contract.get_update_history()
    assert cid in history
    assert isinstance(tx_hash, str)
