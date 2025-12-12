"""
libp2p_node: Async wrapper skeleton around a libp2p host.

NOTES:
- py-libp2p is still evolving and installation differs across environments.
- This file provides a clear, documented skeleton to plug a libp2p host into the rest of the system.
- The module is intentionally minimal: send/receive APIs, peer discovery hook, and a message handler callback.

To use:
- Install a compatible libp2p package (check project README).
- Run under an async event loop (trio or asyncio depending on libp2p implementation).
- Integrate with the aggregator and client by wrapping send/receive calls into async tasks.
"""

from typing import Callable, Optional
import asyncio
import json

# Example assumes a hypothetical py-libp2p API. Adapt to whichever libp2p package you install.
# The code below is illustrative and may need minor changes to match the exact libp2p API.

class LibP2PNode:
    def __init__(self, peer_id: str, listen_multiaddr: str = "/ip4/0.0.0.0/tcp/0"):
        """
        peer_id: unique human-friendly id for your process (not libp2p peer id)
        listen_multiaddr: multiaddr to listen on
        """
        self.peer_id = peer_id
        self.listen_multiaddr = listen_multiaddr
        self.host = None  # underlying libp2p host
        self._running = False
        self._message_handler: Optional[Callable[[str, dict], None]] = None

    async def start(self):
        """
        Start the libp2p host and register protocols.
        """
        # Example pseudo-code — adapt depending on library
        try:
            # from libp2p import new_node
            # self.host = await new_node(listen=self.listen_multiaddr)
            # await self.host.get_network().listen(self.listen_multiaddr)
            self._running = True
            print(f"[libp2p] started node {self.peer_id} (skeleton, adapt to your libp2p package)")
        except Exception as exc:
            print("[libp2p] start failed:", exc)
            raise

    async def stop(self):
        # shutdown host gracefully
        self._running = False
        if self.host:
            try:
                # await self.host.close()
                pass
            except Exception:
                pass

    def on_message(self, handler: Callable[[str, dict], None]):
        """
        Register a callback handler(from_peer_id, message_dict)
        """
        self._message_handler = handler

    async def send(self, peer_multiaddr: str, payload: dict):
        """
        Connect to a peer and send a JSON payload over an agreed protocol.
        """
        # This is illustrative; replace stream creation with actual libp2p API.
        serialized = json.dumps(payload).encode("utf-8")
        # stream = await self.host.new_stream(peer_peer_id, [b"/polyscale/1.0.0"])
        # await stream.write(serialized)
        # await stream.close()

    # Helper to translate incoming libp2p stream to handler call
    async def _handle_incoming(self, peer_id, raw_bytes):
        if self._message_handler is None:
            return
        try:
            msg = json.loads(raw_bytes.decode("utf-8"))
            self._message_handler(peer_id, msg)
        except Exception as e:
            print("[libp2p] incoming parse error:", e)
