from fastapi import APIRouter
from typing import List

router = APIRouter()

# Example in-memory model store
models_store = []

@router.post("/register")
async def register_model(cid: str, round: int):
    models_store.append({"cid": cid, "round": round})
    return {"status": "registered"}

@router.get("/")
async def list_models():
    return models_store
