from fastapi import APIRouter
from typing import List, Dict

router = APIRouter()

# In-memory node status
nodes_status: Dict[str, Dict] = {}

@router.post("/update")
async def update_node_status(node_id: str, status: str):
    nodes_status[node_id] = {"status": status}
    return {"status": "ok"}

@router.get("/")
async def list_nodes():
    return nodes_status
