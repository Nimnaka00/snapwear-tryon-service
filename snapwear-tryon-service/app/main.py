import uvicorn
from fastapi import FastAPI
from app.api.v1.tryon_routes import router as tryon_router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()  # picks up .env

app = FastAPI(title="SnapWear Try-On Service")

# CORS (so your React front end can talk to it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tryon_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
