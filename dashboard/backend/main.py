from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import metrics, nodes, models

app = FastAPI(title="PolyScale-FL Dashboard")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
app.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
app.include_router(models.router, prefix="/models", tags=["models"])

@app.get("/")
async def root():
    return {"message": "PolyScale-FL Dashboard API running"}
