import pytest
from ipfs.ipfs_client import IPFSClient

def test_ipfs_upload_download():
    client = IPFSClient()
    data = {"test": 123}
    cid = client.upload_json(data)
    
    fetched = client.fetch_json(cid)
    assert fetched["test"] == 123
