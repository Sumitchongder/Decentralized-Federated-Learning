import pytest
from networking.p2p_stub import P2PNode

def test_p2p_send_receive():
    node_a = P2PNode(id="A")
    node_b = P2PNode(id="B")
    
    node_a.connect_peer(node_b)
    node_a.send_message("B", "Hello")
    
    msg = node_b.receive_message()
    assert msg == "Hello"
