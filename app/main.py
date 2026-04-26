import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api import api_router, auth_router, charts_router, notifications_router
from .database.models import Base
from .database.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Deribit Price API",
    description="API for fetching and managing \
        cryptocurrency index prices from Deribit",
    version="1.0.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_index():
    return FileResponse(os.path.join("static", "index.html"))

app.include_router(charts_router, prefix="/api/charts")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(notifications_router, prefix="/api/notifications")
app.include_router(api_router, prefix="/api")
