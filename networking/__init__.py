"""
Networking package for PolyScale-FL.

Contains:
- P2PStub: simple in-process message bus for local testing and playgrounds.
- libp2p_node: production-oriented skeleton to integrate py-libp2p (async)
- webrtc_signaling: FastAPI WebRTC signaling server skeleton for browser clients.

Design:
- All networking implementations expose a minimal interface used by the client/aggregator:
    - send_to_aggregator(payload: dict)
    - send(peer_id: str, payload: dict)
    - broadcast(payload: dict)
    - get_peers() -> List[str]
- P2PStub implements the above synchronously and is fully usable in Docker playground.
- libp2p_node and webrtc_signaling are more advanced; they require running additional daemons and dependencies.
"""
__all__ = ["p2p_stub", "libp2p_node", "webrtc_signaling"]
