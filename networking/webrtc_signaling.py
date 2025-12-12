"""
WebRTC Signaling Server Skeleton (FastAPI)

This module implements a tiny signaling server to broker SDP/ICE between browser clients
and an aggregator (or other peers). It uses FastAPI and websockets to relay messages.

Install:
    pip install fastapi uvicorn python-socketio aiohttp

Usage (development):
    uvicorn polyscale_fl.networking.webrtc_signaling:app --host 0.0.0.0 --port 9000

API:
    POST /register -> register a client id
    WebSocket /ws/{client_id} -> exchange SDP messages
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio

app = FastAPI(title="PolyScale-FL WebRTC Signaling")

# simple in-memory registry mapping client_id -> websocket
clients: Dict[str, WebSocket] = {}

@app.post("/register/{client_id}")
async def register_client(client_id: str):
    # in production persist registry and perform auth
    return {"status": "ok", "client_id": client_id}

@app.websocket("/ws/{client_id}")
async def ws_endpoint(ws: WebSocket, client_id: str):
    await ws.accept()
    clients[client_id] = ws
    try:
        while True:
            msg = await ws.receive_text()
            # message must be JSON with target client id
            # forward to target if connected
            import json
            obj = json.loads(msg)
            target = obj.get("target")
            if target and target in clients:
                await clients[target].send_text(msg)
    except WebSocketDisconnect:
        clients.pop(client_id, None)
    except Exception as e:
        clients.pop(client_id, None)
        print("[webrtc_signaling] ws error:", e)
