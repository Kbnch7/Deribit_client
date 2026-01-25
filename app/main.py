from fastapi import FastAPI
from .api.endpoints import router as api_router
from .database.models import Base
from .database.session import engine
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Deribit Price API",
    description="API for fetching and managing cryptocurrency index prices from Deribit",
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

app.include_router(api_router, prefix="/api")