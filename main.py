from fastapi import FastAPI
from dotenv import load_dotenv
from routers.tryon import router as tryon_router

load_dotenv()

app = FastAPI(title="SnapWear Try-On Service")
app.include_router(tryon_router, prefix="/api/v1/tryon", tags=["TryOn"])
