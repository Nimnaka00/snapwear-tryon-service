import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.v1.tryon_routes import router as tryon_router

load_dotenv()  # read .env

app = FastAPI(title="SnapWear Try-On API", version="1.0")

app.include_router(tryon_router, prefix="/api/v1/tryon", tags=["tryon"])

@app.get("/")
async def root():
    return {"message": "SnapWear Try-On backend is up 👟"}
