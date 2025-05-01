from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.tryon_routes import router as tryon_router

app = FastAPI()

# CORS so your React dev (localhost:3000) can call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tryon_router)

# serve temp/ as /static
app.mount("/static", StaticFiles(directory="temp"), name="static")
