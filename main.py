# main.py
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from dotenv import load_dotenv
from routers.tryon import router as tryon_router

load_dotenv()

app = FastAPI(
    title="SnapWear Try-On Service",
    description="Virtual try-on service for clothing items",
    version="1.0.0"
)

# CORS (adjust origins to match your frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173", 
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"  # Remove this in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static directory exists
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    
outputs_dir = os.path.join(static_dir, "outputs")
if not os.path.exists(outputs_dir):
    os.makedirs(outputs_dir)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the try-on router
app.include_router(tryon_router, prefix="/api/v1/tryon", tags=["TryOn"])

# Add redirect for missing trailing slash on tryon endpoint
@app.api_route("/api/v1/tryon", methods=["GET", "POST"])
async def redirect_tryon(request: Request):
    """Redirect /api/v1/tryon to /api/v1/tryon/ to handle missing trailing slash"""
    if request.method == "POST":
        # For POST requests, we can't easily redirect with form data
        # So let's return a helpful error message
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Missing trailing slash. Please use /api/v1/tryon/ instead of /api/v1/tryon",
                "correct_url": "/api/v1/tryon/"
            }
        )
    return RedirectResponse(url="/api/v1/tryon/", status_code=307)

@app.get("/")
async def root():
    return {"message": "SnapWear Try-On Service", "status": "running"}

@app.get("/health")
async def health():
    return {"ok": True, "service": "main"}

# Debug endpoint to list all routes
@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unknown')
            })
    return {"routes": routes}

if __name__ == "__main__":
    import uvicorn
    print("Starting SnapWear Try-On Service...")
    print("Available routes will be:")
    print("- GET  /")
    print("- GET  /health") 
    print("- POST /api/v1/tryon/")
    print("- GET  /api/v1/tryon/health")
    print("- GET  /debug/routes")
    uvicorn.run(app, host="0.0.0.0", port=8000)