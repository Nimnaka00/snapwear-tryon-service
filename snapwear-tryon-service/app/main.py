from fastapi import FastAPI
from dotenv import load_dotenv
from api.v1 import tryon_routes

load_dotenv()

app = FastAPI(
    title="SnapWear Virtual Try-On API",
    version="1.0.0"
)

app.include_router(tryon_routes.router, prefix="/api/v1", tags=["Try-On"])
